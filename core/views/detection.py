import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from core.models import DetectionHistory, Alert, AuditLog
from core.decorators import analyst_required
from services.ml_service import ml_service
from services.notification_service import notification_service


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
            )

            if result['threat_category'] == 'attack' and result['confidence'] >= 0.6:
                Alert.objects.create(detection=detection, severity=threat_level)

                # Send notification (Telegram / Email)
                try:
                    feature_dict = {
                        'altitude': features[0], 'speed': features[1],
                        'signal_strength': features[3], 'gps_accuracy': features[9],
                        'vibration': features[8], 'temperature': features[7],
                    }
                    notification_service.send_threat_alert(
                        prediction=result['prediction'],
                        confidence=result['confidence'],
                        threat_level=threat_level,
                        features=feature_dict,
                        detection_id=detection.id,
                    )
                except Exception:
                    pass  # Don't fail detection if notification fails

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
    results = []
    total = threat_count = 0

    if request.method == 'POST' and request.FILES.get('file'):
        import pandas as pd
        import io

        try:
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Only CSV files are supported.')
                return redirect('batch_detect')

            df = pd.read_csv(io.StringIO(csv_file.read().decode('utf-8')))

            feature_cols = [
                'altitude', 'speed', 'direction', 'signal_strength',
                'distance_from_base', 'flight_time', 'battery_level',
                'temperature', 'vibration', 'gps_accuracy',
            ]
            missing = [c for c in feature_cols if c not in df.columns]
            if missing:
                messages.error(request, f'CSV missing columns: {", ".join(missing)}')
                return redirect('batch_detect')

            for _, row in df.iterrows():
                features = [float(row[c]) for c in feature_cols]
                try:
                    result = ml_service.predict(features)
                    threat_level = ml_service.calculate_threat_level(
                        result['prediction'], result['confidence']
                    )
                    results.append({
                        'features': {c: round(float(row[c]), 2) for c in feature_cols},
                        'prediction': result['prediction'],
                        'confidence': result['confidence'],
                        'threat_level': threat_level,
                        'is_threat': result['threat_category'] == 'attack',
                    })
                    if result['threat_category'] == 'attack':
                        threat_count += 1
                except Exception:
                    results.append({
                        'features': {c: round(float(row[c]), 2) for c in feature_cols},
                        'prediction': 'Error',
                        'confidence': 0,
                        'threat_level': 'Unknown',
                        'is_threat': False,
                    })

            total = len(results)
            messages.success(
                request,
                f'Batch complete: {total} samples processed, {threat_count} threats detected.'
            )

        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')

    return render(request, 'detection/batch.html', {
        'results': results,
        'total': total,
        'threat_count': threat_count,
    })
