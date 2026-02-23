from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from core.models import User, AuditLog
from core.decorators import admin_required


@login_required
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    return render(request, 'admin/dashboard.html', {
        'total_users': total_users,
        'active_users': active_users,
    })


@login_required
@admin_required
def users_list(request):
    qs = User.objects.order_by('-created_at')
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'admin/users.html', {
        'users': page.object_list,
        'pagination': page,
    })


@login_required
@admin_required
def toggle_user_active(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_users')
