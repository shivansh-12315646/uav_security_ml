"""Admin panel routes."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.extensions import db
from app.models.user import User
from app.models.audit import AuditLog
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page."""
    page = request.args.get('page', 1, type=int)
    users_query = User.query.order_by(User.created_at.desc())
    pagination = users_query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html',
                         users=pagination.items,
                         pagination=pagination)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status."""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))
