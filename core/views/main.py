from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count
from core.models import DetectionHistory, Alert, MLModel, MitigationEvent


@login_required
def index(request):
    return redirect('dashboard_overview')


@login_required
def dashboard(request):
    return redirect('dashboard_overview')


@login_required
def dashboard_overview(request):
    try:
        yesterday = timezone.now() - timedelta(days=1)
        total_detections = DetectionHistory.objects.count()
        detections_today = DetectionHistory.objects.filter(timestamp__gte=yesterday).count()
        total_threats = DetectionHistory.objects.exclude(prediction='Normal').count()
        threats_today = DetectionHistory.objects.filter(timestamp__gte=yesterday).exclude(prediction='Normal').count()
        active_alerts = Alert.objects.filter(status__in=['Open', 'Acknowledged']).count()
        critical_alerts = Alert.objects.filter(
            status__in=['Open', 'Acknowledged'],
            detection__threat_level='Critical'
        ).count()
        threat_rate = (total_threats / total_detections * 100) if total_detections > 0 else 0
        avg_confidence = DetectionHistory.objects.aggregate(avg=Avg('confidence'))['avg'] or 0
        recent_detections = DetectionHistory.objects.select_related('user').order_by('-timestamp')[:10]
        recent_alerts = Alert.objects.order_by('-created_at')[:5]
        active_model = MLModel.objects.filter(is_active=True).first()
        detection_trend = []
        for i in range(6, -1, -1):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = DetectionHistory.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end).count()
            detection_trend.append({'date': day_start.strftime('%Y-%m-%d'), 'count': count})

        # Countermeasure context for dashboard
        latest_detection = DetectionHistory.objects.order_by('-timestamp').first()
        current_fusion_threat_level = latest_detection.fusion_threat_level if latest_detection else 0
        recent_mitigations = MitigationEvent.objects.select_related('detection').order_by('-timestamp')[:5]
        total_responses = MitigationEvent.objects.count()
        successful_responses = MitigationEvent.objects.filter(success=True).count()
        response_success_rate = (
            round(successful_responses / total_responses * 100, 1) if total_responses > 0 else 0
        )
        active_countermeasures = list(
            MitigationEvent.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).values_list('action_taken', flat=True).distinct()
        )
    except Exception:
        total_detections = detections_today = total_threats = threats_today = 0
        active_alerts = critical_alerts = 0
        threat_rate = avg_confidence = 0.0
        recent_detections = recent_alerts = []
        active_model = None
        detection_trend = []
        current_fusion_threat_level = 0
        recent_mitigations = []
        response_success_rate = 0
        active_countermeasures = []

    return render(request, 'dashboard/overview.html', {
        'total_detections': total_detections,
        'detections_today': detections_today,
        'total_threats': total_threats,
        'threats_today': threats_today,
        'active_alerts': active_alerts,
        'critical_alerts': critical_alerts,
        'threat_rate': threat_rate,
        'avg_confidence': avg_confidence,
        'recent_detections': recent_detections,
        'recent_alerts': recent_alerts,
        'active_model': active_model,
        'detection_trend': detection_trend,
        'current_fusion_threat_level': current_fusion_threat_level,
        'recent_mitigations': recent_mitigations,
        'response_success_rate': response_success_rate,
        'active_countermeasures': active_countermeasures,
    })


@login_required
def algorithms(request):
    return render(request, 'algorithms.html')
