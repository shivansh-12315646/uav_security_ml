"""
Views for real drone connection / system integration.

Provides:
  - Dashboard showing connected drones and live status
  - REST API endpoint for drones to POST telemetry
  - Drone registration and management
"""
import json
import uuid
import logging
from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from core.models import DroneDevice, DroneTelemetry, DetectionHistory, Alert
from services.ml_service import ml_service
from services.notification_service import notification_service

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'Unknown')


# ──────────────────────────────────────────────────────────────────────
# Page views
# ──────────────────────────────────────────────────────────────────────

@login_required
def drone_dashboard(request):
    """Main drone connection dashboard."""
    devices = DroneDevice.objects.all().order_by('-last_seen')

    # Update statuses based on heartbeat
    cutoff = timezone.now() - timedelta(seconds=60)
    for device in devices:
        if device.last_seen and device.last_seen < cutoff and device.status == 'online':
            device.status = 'offline'
            device.save(update_fields=['status'])

    # Recent telemetry
    recent_telemetry = DroneTelemetry.objects.select_related('device').order_by('-timestamp')[:50]

    # Stats
    online_count = devices.filter(status='online').count()
    total_count = devices.count()
    threats_today = DroneTelemetry.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=1),
        is_threat=True
    ).count()
    total_telemetry = DroneTelemetry.objects.count()

    context = {
        'devices': devices,
        'recent_telemetry': recent_telemetry,
        'online_count': online_count,
        'total_count': total_count,
        'threats_today': threats_today,
        'total_telemetry': total_telemetry,
        'notification_status': notification_service.get_status(),
    }
    return render(request, 'drone/connection.html', context)


# ──────────────────────────────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────────────────────────────

@login_required
@require_http_methods(['POST'])
def register_drone(request):
    """Register a new drone device and get an API key."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        data = request.POST

    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Drone name is required'}, status=400)

    # Check for duplicate name
    if DroneDevice.objects.filter(name=name).exists():
        return JsonResponse({'error': f'Drone "{name}" already registered'}, status=400)

    api_key = uuid.uuid4().hex
    device = DroneDevice.objects.create(
        name=name,
        api_key=api_key,
        registered_by=request.user,
        description=data.get('description', ''),
    )

    return JsonResponse({
        'success': True,
        'device_id': device.id,
        'name': device.name,
        'api_key': api_key,
        'message': f'Drone "{name}" registered successfully. Save the API key!'
    })


@csrf_exempt
@require_http_methods(['POST'])
def drone_telemetry(request):
    """
    REST API endpoint for drones to POST telemetry data.

    Authenticates via X-API-Key header.
    Accepts JSON body with 10 UAV feature values.
    Runs ML prediction and returns threat assessment.
    """
    # Authenticate via API key
    api_key = request.META.get('HTTP_X_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'X-API-Key header required'}, status=401)

    try:
        device = DroneDevice.objects.get(api_key=api_key)
    except DroneDevice.DoesNotExist:
        return JsonResponse({'error': 'Invalid API key'}, status=401)

    # Parse telemetry data
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    required_fields = [
        'altitude', 'speed', 'direction', 'signal_strength',
        'distance_from_base', 'flight_time', 'battery_level',
        'temperature', 'vibration', 'gps_accuracy'
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return JsonResponse({'error': f'Missing fields: {", ".join(missing)}'}, status=400)

    try:
        features = [float(data[f]) for f in required_fields]

        # Run ML prediction
        result = ml_service.predict(features)
        threat_level = ml_service.calculate_threat_level(result['prediction'], result['confidence'])

        is_threat = result['threat_category'] == 'attack'

        # Save telemetry record
        telemetry = DroneTelemetry.objects.create(
            device=device,
            altitude=features[0],
            speed=features[1],
            direction=features[2],
            signal_strength=features[3],
            distance_from_base=features[4],
            flight_time=features[5],
            battery_level=features[6],
            temperature=features[7],
            vibration=features[8],
            gps_accuracy=features[9],
            prediction=result['prediction'],
            confidence=result['confidence'],
            threat_level=threat_level,
            is_threat=is_threat,
        )

        # Also save to DetectionHistory for main dashboard
        if device.registered_by:
            detection = DetectionHistory.objects.create(
                user=device.registered_by,
                altitude=features[0],
                speed=features[1],
                direction=features[2],
                signal_strength=features[3],
                distance_from_base=features[4],
                flight_time=features[5],
                battery_level=features[6],
                temperature=features[7],
                vibration=features[8],
                gps_accuracy=features[9],
                prediction=result['prediction'],
                confidence=result['confidence'],
                threat_level=threat_level,
                model_version=result['model_used'],
                ip_address=_get_client_ip(request),
                notes=f'From drone: {device.name}',
            )

            # Create alert for threats
            if is_threat and result['confidence'] >= 0.6:
                Alert.objects.create(detection=detection, severity=threat_level)

        # Update device heartbeat
        device.last_seen = timezone.now()
        device.status = 'online'
        device.save(update_fields=['last_seen', 'status'])

        # Send notification for threats
        if is_threat:
            feature_dict = {f: float(data[f]) for f in required_fields}
            notification_service.send_threat_alert(
                prediction=result['prediction'],
                confidence=result['confidence'],
                threat_level=threat_level,
                features=feature_dict,
                detection_id=telemetry.id,
            )

        return JsonResponse({
            'success': True,
            'telemetry_id': telemetry.id,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'threat_level': threat_level,
            'is_threat': is_threat,
            'model_used': result['model_used'],
            'timestamp': telemetry.timestamp.isoformat(),
        })

    except Exception as e:
        logger.error(f"Drone telemetry error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def drone_heartbeat(request):
    """Heartbeat endpoint for drones to check connectivity."""
    api_key = request.META.get('HTTP_X_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'X-API-Key required'}, status=401)

    try:
        device = DroneDevice.objects.get(api_key=api_key)
        device.last_seen = timezone.now()
        device.status = 'online'
        device.save(update_fields=['last_seen', 'status'])
        return JsonResponse({
            'status': 'ok',
            'device': device.name,
            'server_time': timezone.now().isoformat(),
        })
    except DroneDevice.DoesNotExist:
        return JsonResponse({'error': 'Invalid API key'}, status=401)


@login_required
@require_http_methods(['POST'])
def delete_drone(request, device_id):
    """Delete a registered drone device."""
    try:
        device = DroneDevice.objects.get(id=device_id)
        device.delete()
        return JsonResponse({'success': True})
    except DroneDevice.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)


@login_required
def test_notification(request):
    """Send a test notification to verify configuration."""
    result = notification_service.send_test_notification()
    return JsonResponse(result)


@login_required
def drone_telemetry_history(request, device_id):
    """Get recent telemetry for a specific drone."""
    try:
        device = DroneDevice.objects.get(id=device_id)
    except DroneDevice.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

    records = DroneTelemetry.objects.filter(device=device).order_by('-timestamp')[:100]
    data = []
    for r in records:
        data.append({
            'id': r.id,
            'timestamp': r.timestamp.isoformat(),
            'prediction': r.prediction,
            'confidence': round(r.confidence, 4),
            'threat_level': r.threat_level,
            'is_threat': r.is_threat,
            'altitude': r.altitude,
            'speed': r.speed,
            'signal_strength': r.signal_strength,
            'gps_accuracy': r.gps_accuracy,
        })

    return JsonResponse({'device': device.name, 'telemetry': data})
