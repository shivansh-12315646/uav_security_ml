import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from core.models import User, AuditLog


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'Unknown')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_overview')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated.')
                return render(request, 'auth/login.html')
            login(request, user)
            user.update_last_login()
            AuditLog.objects.create(
                user=user, action='login',
                details='{"success": true}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'dashboard_overview')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_overview')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/register.html')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth/register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register.html')

        user = User.objects.create_user(username=username, email=email, password=password, role='viewer')
        AuditLog.objects.create(
            user=user, action='register',
            details=json.dumps({'email': email}),
            ip_address=get_client_ip(request)
        )
        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('auth_login')

    return render(request, 'auth/register.html')


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user, action='logout',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('auth_login')
