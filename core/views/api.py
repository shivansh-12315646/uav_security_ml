import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from core.models import DetectionHistory, Alert
from services.ml_service import ml_service


@login_required
@csrf_exempt
@require_http_methods(['POST'])
def api_detect(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'error': 'No data provided'}, status=400)

    required = ['altitude', 'speed', 'direction', 'signal_strength', 'distance_from_base',
                'flight_time', 'battery_level', 'temperature', 'vibration', 'gps_accuracy']
    if not all(f in data for f in required):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        features = [float(data[f]) for f in required]
        result = ml_service.predict(features)
        threat_level = ml_service.calculate_threat_level(result['prediction'], result['confidence'])

        detection = DetectionHistory.objects.create(
            user=request.user,
            packet_size=features[0], inter_arrival=features[1],
            packet_rate=features[2], duration=features[3],
            failed_logins=features[4],
            prediction=result['prediction'],
            confidence=result['confidence'],
            threat_level=threat_level,
            model_version=result['model_used'],
        )
        return JsonResponse({
            'success': True,
            'detection_id': detection.id,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'threat_level': threat_level,
            'model_used': result['model_used'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_history(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    qs = DetectionHistory.objects.order_by('-timestamp')
    total = qs.count()
    start = (page - 1) * per_page
    items = list(qs[start:start + per_page])
    return JsonResponse({
        'detections': [d.to_dict() for d in items],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page,
    })


@login_required
def api_alerts(request):
    status = request.GET.get('status', 'Open')
    qs = Alert.objects.all()
    if status != 'All':
        qs = qs.filter(status=status)
    alerts = list(qs.order_by('-created_at')[:50])
    return JsonResponse({'alerts': [a.to_dict() for a in alerts]})


def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'UAV Security ML', 'version': '3.0.0'})
