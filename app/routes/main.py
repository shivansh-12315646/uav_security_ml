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
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Total detections
        total_detections = DetectionHistory.query.count()
        detections_today = DetectionHistory.query.filter(
            DetectionHistory.timestamp >= yesterday
        ).count()
        
        # Threat statistics
        total_threats = DetectionHistory.query.filter_by(prediction='Threat').count()
        threats_today = DetectionHistory.query.filter(
            DetectionHistory.prediction == 'Threat',
            DetectionHistory.timestamp >= yesterday
        ).count()
        
        # Alert statistics
        active_alerts = Alert.query.filter(
            Alert.status.in_(['Open', 'Acknowledged'])
        ).count()
        
        critical_alerts = Alert.query.join(DetectionHistory, Alert.detection_id == DetectionHistory.id).filter(
            Alert.status.in_(['Open', 'Acknowledged']),
            DetectionHistory.threat_level == 'Critical'
        ).count()
        
        # Threat detection rate
        threat_rate = (total_threats / total_detections * 100) if total_detections > 0 else 0
        
        # Recent detections and alerts
        recent_detections = DetectionHistory.query.order_by(DetectionHistory.timestamp.desc()).limit(10).all()
        recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
        
        # Active model info
        active_model = MLModel.query.filter_by(is_active=True).first()
        
        # Calculate average confidence
        avg_confidence = db.session.query(func.avg(DetectionHistory.confidence)).scalar()
        avg_confidence = float(avg_confidence) if avg_confidence else 0
        
        # Detection trend for chart (last 7 days)
        detection_trend = []
        for i in range(6, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = DetectionHistory.query.filter(
                DetectionHistory.timestamp >= day_start,
                DetectionHistory.timestamp < day_end
            ).count()
            
            detection_trend.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
    except Exception:
        # Fallback to demo data if tables don't exist yet
        total_detections = 0
        detections_today = 0
        total_threats = 0
        threats_today = 0
        active_alerts = 0
        critical_alerts = 0
        threat_rate = 0.0
        avg_confidence = 0.0
        recent_detections = []
        recent_alerts = []
        active_model = None
        detection_trend = []
    
    return render_template('dashboard/overview.html',
                         total_detections=total_detections,
                         detections_today=detections_today,
                         total_threats=total_threats,
                         threats_today=threats_today,
                         active_alerts=active_alerts,
                         critical_alerts=critical_alerts,
                         threat_rate=threat_rate,
                         avg_confidence=avg_confidence,
                         recent_detections=recent_detections,
                         recent_alerts=recent_alerts,
                         active_model=active_model,
                         detection_trend=detection_trend)


@main_bp.route('/algorithms')
def algorithms():
    """ML algorithms comparison page."""
    return render_template('algorithms.html')


