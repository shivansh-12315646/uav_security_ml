"""Custom decorators for authentication and authorization."""
from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """
    Decorator to require specific role.
    
    Args:
        role: Required role ('admin', 'analyst', 'viewer')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not current_user.can_access(role):
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required('admin')(f)


def analyst_required(f):
    """Decorator to require analyst role or higher."""
    return role_required('analyst')(f)
