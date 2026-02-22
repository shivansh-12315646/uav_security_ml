from core.models import Alert


def active_alerts_count(request):
    """Add active alerts count to all template contexts."""
    if request.user.is_authenticated:
        try:
            count = Alert.objects.filter(status__in=['Open', 'Acknowledged']).count()
        except Exception:
            count = 0
        return {'active_alerts_count': count}
    return {'active_alerts_count': 0}
