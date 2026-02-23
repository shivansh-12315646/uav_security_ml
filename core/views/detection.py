import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from core.models import DetectionHistory, Alert, AuditLog
from core.decorators import analyst_required
from services.ml_service import ml_service


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'Unknown')


@login_required
@analyst_required
def detect(request):
    prediction_result = None

    if request.method == 'POST':
        try:
            features = [
                float(request.POST.get('altitude', 0)),
                float(request.POST.get('speed', 0)),
                float(request.POST.get('direction', 0)),
                float(request.POST.get('signal_strength', 0)),
                float(request.POST.get('distance_from_base', 0)),
                float(request.POST.get('flight_time', 0)),
                float(request.POST.get('battery_level', 0)),
                float(request.POST.get('temperature', 0)),
                float(request.POST.get('vibration', 0)),
                float(request.POST.get('gps_accuracy', 0)),
            ]

            result = ml_service.predict(features)
            threat_level = ml_service.calculate_threat_level(result['prediction'], result['confidence'])

            detection = DetectionHistory.objects.create(
                user=request.user,
                packet_size=features[0],
                inter_arrival=features[1],
                packet_rate=features[2],
                duration=features[3],
                failed_logins=features[4],
                prediction=result['prediction'],
                confidence=result['confidence'],
                threat_level=threat_level,
                model_version=result['model_used'],
                ip_address=get_client_ip(request),
            )

            if result['threat_category'] == 'attack' and result['confidence'] >= 0.6:
                Alert.objects.create(detection=detection, severity=threat_level)

            AuditLog.objects.create(
                user=request.user, action='detection',
                details=json.dumps({'prediction': result['prediction'], 'confidence': result['confidence'], 'threat_level': threat_level}),
                ip_address=get_client_ip(request)
            )

            prediction_result = {**result, 'threat_level': threat_level, 'detection_id': detection.id}
            level = 'success' if result['threat_category'] == 'normal' else 'warning'
            messages.add_message(request, getattr(messages, level.upper()),
                f'Detection completed: {result["prediction"]} (Confidence: {result["confidence"]:.2%})')

        except Exception as e:
            messages.error(request, f'Error during detection: {str(e)}')

    return render(request, 'detection/detect.html', {'prediction': prediction_result})


@login_required
def history(request):
    prediction_filter = request.GET.get('prediction')
    threat_level_filter = request.GET.get('threat_level')

    qs = DetectionHistory.objects.select_related('user').all()
    if prediction_filter:
        qs = qs.filter(prediction=prediction_filter)
    if threat_level_filter:
        qs = qs.filter(threat_level=threat_level_filter)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    # Pre-compute counts for template stats
    threat_count = DetectionHistory.objects.exclude(prediction='Normal').count()
    normal_count = DetectionHistory.objects.filter(prediction='Normal').count()

    return render(request, 'detection/history.html', {
        'detections': page.object_list,
        'pagination': page,
        'prediction_filter': prediction_filter,
        'threat_level_filter': threat_level_filter,
        'threat_count': threat_count,
        'normal_count': normal_count,
    })


@login_required
@analyst_required
def batch_detect(request):
    if request.method == 'POST':
        messages.info(request, 'Batch processing feature coming soon!')
        return redirect('batch_detect')
    return render(request, 'detection/batch.html')
