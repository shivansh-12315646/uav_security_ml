from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from core.models import DetectionHistory


@login_required
def analytics(request):
    return render(request, 'dashboard/analytics.html')


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
