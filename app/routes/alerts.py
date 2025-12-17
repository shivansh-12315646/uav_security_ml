"""Alert management routes."""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.alert import Alert
from app.models.detection import DetectionHistory
from app.utils.decorators import analyst_required

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')


@alerts_bp.route('/')
@login_required
def alerts_list():
    """List all alerts with filtering."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'Open')
    
    query = Alert.query
    
    if status_filter and status_filter != 'All':
        query = query.filter_by(status=status_filter)
    
    query = query.order_by(Alert.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('alerts/list.html',
                         alerts=pagination.items,
                         pagination=pagination,
                         status_filter=status_filter)


@alerts_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@analyst_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert."""
    alert = Alert.query.get_or_404(alert_id)
    alert.acknowledge(current_user.id)
    flash('Alert acknowledged.', 'success')
    return redirect(url_for('alerts.alerts_list'))


@alerts_bp.route('/<int:alert_id>/resolve', methods=['POST'])
@login_required
@analyst_required
def resolve_alert(alert_id):
    """Resolve an alert."""
    alert = Alert.query.get_or_404(alert_id)
    notes = request.form.get('notes')
    alert.resolve(notes)
    flash('Alert resolved.', 'success')
    return redirect(url_for('alerts.alerts_list'))
