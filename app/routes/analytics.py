"""Analytics routes for advanced data visualization."""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
from app.models.detection import DetectionHistory
from app.models.alert import Alert
from sqlalchemy import func
from app.extensions import db

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def analytics():
    """Advanced analytics dashboard."""
    return render_template('dashboard/analytics.html')


@analytics_bp.route('/api/detection-timeline')
@login_required
def detection_timeline():
    """API endpoint for detection timeline data."""
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query detections grouped by date
    results = db.session.query(
        func.date(DetectionHistory.timestamp).label('date'),
        DetectionHistory.prediction,
        func.count(DetectionHistory.id).label('count')
    ).filter(
        DetectionHistory.timestamp >= start_date
    ).group_by(
        func.date(DetectionHistory.timestamp),
        DetectionHistory.prediction
    ).all()
    
    return jsonify([{
        'date': r.date.isoformat(),
        'prediction': r.prediction,
        'count': r.count
    } for r in results])
