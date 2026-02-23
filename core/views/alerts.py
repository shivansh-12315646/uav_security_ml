from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from core.models import Alert
from core.decorators import analyst_required


@login_required
def alerts_list(request):
    status_filter = request.GET.get('status', 'Open')
    qs = Alert.objects.select_related('detection').all()
    if status_filter and status_filter != 'All':
        qs = qs.filter(status=status_filter)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    # Pre-compute status counts for template
    open_count = Alert.objects.filter(status='Open').count()
    acknowledged_count = Alert.objects.filter(status='Acknowledged').count()
    resolved_count = Alert.objects.filter(status='Resolved').count()

    return render(request, 'alerts/list.html', {
        'alerts': page.object_list,
        'pagination': page,
        'status_filter': status_filter,
        'open_count': open_count,
        'acknowledged_count': acknowledged_count,
        'resolved_count': resolved_count,
    })


@login_required
@analyst_required
def acknowledge_alert(request, alert_id):
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        alert.acknowledge(request.user.id)
        messages.success(request, 'Alert acknowledged.')
    return redirect('alerts_list')


@login_required
@analyst_required
def resolve_alert(request, alert_id):
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        notes = request.POST.get('notes')
        alert.resolve(notes)
        messages.success(request, 'Alert resolved.')
    return redirect('alerts_list')
