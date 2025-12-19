"""
Main routes for dashboard and overview.
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.extensions import db
from app.models.detection import DetectionHistory
from app.models.alert import Alert
from app.models.ml_model import MLModel
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page - redirect to login or dashboard."""
    if current_user.is_authenticated:
        return render_template('dashboard/overview.html')
    return render_template('auth/login.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with overview metrics."""
    # Calculate metrics for last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    last_week = datetime.utcnow() - timedelta(days=7)
    
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
    
    critical_alerts = Alert.query.join(DetectionHistory).filter(
        Alert.status.in_(['Open', 'Acknowledged']),
        DetectionHistory.threat_level == 'Critical'
    ).count()
    
    # Threat detection rate
    threat_rate = (total_threats / total_detections * 100) if total_detections > 0 else 0
    
    # Recent detections
    recent_detections = DetectionHistory.query.order_by(
        DetectionHistory.timestamp.desc()
    ).limit(10).all()
    
    # Recent alerts
    recent_alerts = Alert.query.order_by(
        Alert.created_at.desc()
    ).limit(5).all()
    
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

