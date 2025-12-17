"""
Authentication routes for login, logout, and registration.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db, limiter
from app.models.user import User
from app.models.audit import AuditLog
from app.utils.helpers import get_client_ip

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            # Log login action
            audit = AuditLog(
                user_id=user.id,
                action='login',
                details={'success': True},
                ip_address=get_client_ip(request),
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            # Log failed login
            if user:
                audit = AuditLog(
                    user_id=user.id,
                    action='login_failed',
                    details={'reason': 'invalid_password'},
                    ip_address=get_client_ip(request),
                    user_agent=request.headers.get('User-Agent')
                )
                db.session.add(audit)
                db.session.commit()
            
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    """Registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        # Create new user with 'viewer' role by default
        user = User(username=username, email=email, password=password, role='viewer')
        db.session.add(user)
        db.session.commit()
        
        # Log registration
        audit = AuditLog(
            user_id=user.id,
            action='register',
            details={'email': email},
            ip_address=get_client_ip(request),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Logout handler."""
    if current_user.is_authenticated:
        # Log logout
        audit = AuditLog(
            user_id=current_user.id,
            action='logout',
            ip_address=get_client_ip(request),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit)
        db.session.commit()
        
        logout_user()
        flash('You have been logged out.', 'info')
    
    return redirect(url_for('auth.login'))
