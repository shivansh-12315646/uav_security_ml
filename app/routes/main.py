"""
Main routes for dashboard and overview.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.extensions import db
from app.models.detection import DetectionHistory
from app.models.alert import Alert
from app.models.ml_model import MLModel
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Redirect to enhanced dashboard overview."""
    return redirect(url_for('main.dashboard_overview'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirect old dashboard to new overview."""
    return redirect(url_for('main.dashboard_overview'))


@main_bp.route('/dashboard/overview')
@login_required
def dashboard_overview():
    """Enhanced dashboard overview page."""
    # Get statistics (with safe defaults)
    try:
        total_detections = DetectionHistory.query.count()
        threats_detected = DetectionHistory.query.filter_by(prediction='Threat').count()
        active_alerts = Alert.query.filter_by(status='Open').count()
        recent_detections = DetectionHistory.query.order_by(DetectionHistory.timestamp.desc()).limit(10).all()
        recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
        threat_rate = (threats_detected / total_detections * 100) if total_detections > 0 else 0
    except Exception:
        # Fallback to demo data if tables don't exist yet
        total_detections = 0
        threats_detected = 0
        active_alerts = 0
        threat_rate = 0.0
        recent_detections = []
        recent_alerts = []
    
    return render_template('dashboard/overview.html',
                         total_detections=total_detections,
                         threats_detected=threats_detected,
                         active_alerts=active_alerts,
                         threat_rate=threat_rate,
                         recent_detections=recent_detections,
                         recent_alerts=recent_alerts)


@main_bp.route('/algorithms')
def algorithms():
    """ML algorithms comparison page."""
    return render_template('algorithms.html')


