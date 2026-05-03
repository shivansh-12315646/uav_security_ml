import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count
from core.models import DetectionHistory, Alert, MLModel


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

        # 30-day trend
        detection_trend_30 = []
        for i in range(29, -1, -1):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = DetectionHistory.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end).count()
            detection_trend_30.append({'date': day_start.strftime('%Y-%m-%d'), 'count': count})

        # 90-day trend
        detection_trend_90 = []
        for i in range(89, -1, -1):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = DetectionHistory.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end).count()
            detection_trend_90.append({'date': day_start.strftime('%Y-%m-%d'), 'count': count})
    except Exception:
        total_detections = detections_today = total_threats = threats_today = 0
        active_alerts = critical_alerts = 0
        threat_rate = avg_confidence = 0.0
        recent_detections = recent_alerts = []
        active_model = None
        detection_trend = []
        detection_trend_30 = []
        detection_trend_90 = []

    # Load unsupervised results summary
    unsupervised_stats = {}
    try:
        import json as _json
        results_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'exports', 'unsupervised_results.json'
        )
        if os.path.exists(results_path):
            with open(results_path) as _f:
                _ur = _json.load(_f)
            unsupervised_stats = {
                'kmeans_k': _ur.get('kmeans', {}).get('best_k', '—'),
                'anomaly_count': _ur.get('isolation_forest', {}).get('n_anomalies', 0),
                'anomaly_rate': _ur.get('isolation_forest', {}).get('anomaly_rate', 0),
                'silhouette': round(
                    _ur.get('kmeans', {}).get('metrics', {}).get('silhouette_score', 0), 4
                ),
            }
    except Exception:
        pass

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
        'detection_trend_30': detection_trend_30,
        'detection_trend_90': detection_trend_90,
        **unsupervised_stats,
    })


@login_required
def algorithms(request):
    return render(request, 'algorithms.html')
