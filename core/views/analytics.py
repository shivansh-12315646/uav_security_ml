import os
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from core.models import DetectionHistory


@login_required
def analytics(request):
    """Analytics dashboard with real data from detections and unsupervised results."""
    # Detection stats
    total_detections = DetectionHistory.objects.count()
    total_threats = DetectionHistory.objects.exclude(prediction='Normal').count()
    avg_confidence = DetectionHistory.objects.aggregate(avg=Avg('confidence'))['avg'] or 0

    # Threat distribution from DB
    threat_dist = list(
        DetectionHistory.objects
        .values('prediction')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # Load unsupervised results
    unsupervised = {}
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    results_path = os.path.join(base, 'exports', 'unsupervised_results.json')
    if os.path.exists(results_path):
        try:
            with open(results_path) as f:
                unsupervised = json.load(f)
        except Exception:
            pass

    context = {
        'total_detections': total_detections,
        'total_threats': total_threats,
        'avg_confidence': round(avg_confidence * 100, 1) if avg_confidence else 0,
        'threat_dist_json': threat_dist,
        'unsupervised_json': unsupervised,
        'has_unsupervised': bool(unsupervised),
    }
    return render(request, 'dashboard/analytics.html', context)


@login_required
def detection_timeline(request):
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)

    results = (
        DetectionHistory.objects
        .filter(timestamp__gte=start_date)
        .annotate(date=TruncDate('timestamp'))
        .values('date', 'prediction')
        .annotate(count=Count('id'))
    )

    data = [{'date': str(r['date']), 'prediction': r['prediction'], 'count': r['count']} for r in results]
    return JsonResponse(data, safe=False)
