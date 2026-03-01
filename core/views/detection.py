import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from core.models import DetectionHistory, Alert, AuditLog, MitigationEvent
from core.decorators import analyst_required
from services.ml_service import ml_service
from services.fusion_engine import fusion_engine
from services.autonomous_response import autonomous_response


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

            # Fusion engine: combine RF + GNSS indicators into a unified threat score.
            # GNSS attacks are identified by matching against known attack type labels.
            _GNSS_ATTACK_LABELS = {'gps_spoofing', 'gnss_spoofing', 'gps-spoofing', 'gnss-spoofing'}
            is_gnss_attack = str(result['prediction']).lower().replace(' ', '_') in _GNSS_ATTACK_LABELS
            rf_score = result['confidence'] if result['threat_category'] == 'attack' else 0.0
            gnss_score = result['confidence'] if is_gnss_attack else 0.0
            fusion_result = fusion_engine.calculate_combined_threat(
                rf_score=rf_score,
                gnss_score=gnss_score,
                attack_type=result['prediction'],
            )
            fusion_threat_level = fusion_result['threat_level']

            # Autonomous response: execute countermeasures when threat level >= 2
            response_result = None
            if fusion_threat_level >= 2:
                response_result = autonomous_response.execute_response(
                    threat_level=fusion_threat_level,
                    attack_context=fusion_result,
                )

            mitigation_action = ''
            response_success = False
            operator_notified = False
            response_ts = None
            if response_result:
                mitigation_action = response_result.get('response_summary', '')
                response_success = response_result.get('success', False)
                operator_notified = response_result.get('operator_notified', False)
                response_ts = timezone.now()

            detection = DetectionHistory.objects.create(
                user=request.user,
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
                ip_address=get_client_ip(request),
                fusion_threat_level=fusion_threat_level,
                combined_threat_score=fusion_result['combined_score'],
                mitigation_action=mitigation_action,
                response_timestamp=response_ts,
                response_success=response_success,
                operator_notified=operator_notified,
            )

            if result['threat_category'] == 'attack' and result['confidence'] >= 0.6:
                Alert.objects.create(detection=detection, severity=threat_level)

            # Log each mitigation action as a MitigationEvent
            if response_result:
                for action in response_result.get('actions_taken', []):
                    MitigationEvent.objects.create(
                        detection=detection,
                        threat_level=fusion_threat_level,
                        action_taken=action,
                        success=response_result.get('success', False),
                        operator_notified=response_result.get('operator_notified', False),
                    )

            AuditLog.objects.create(
                user=request.user, action='detection',
                details=json.dumps({
                    'prediction': result['prediction'],
                    'confidence': result['confidence'],
                    'threat_level': threat_level,
                    'fusion_threat_level': fusion_threat_level,
                    'mitigation_action': mitigation_action,
                }),
                ip_address=get_client_ip(request)
            )

            prediction_result = {
                **result,
                'threat_level': threat_level,
                'detection_id': detection.id,
                'fusion_threat_level': fusion_threat_level,
                'combined_threat_score': fusion_result['combined_score'],
                'fusion_description': fusion_result['threat_description'],
                'mitigation_action': mitigation_action,
                'response_actions': response_result.get('actions_taken', []) if response_result else [],
            }
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
