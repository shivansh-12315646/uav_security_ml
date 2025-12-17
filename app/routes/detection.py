"""
Detection routes for UAV threat detection operations.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.detection import DetectionHistory
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.services.ml_service import ml_service
from app.utils.decorators import analyst_required
from app.utils.helpers import get_client_ip

detection_bp = Blueprint('detection', __name__, url_prefix='/detection')


@detection_bp.route('/detect', methods=['GET', 'POST'])
@login_required
@analyst_required
def detect():
    """Single UAV detection page."""
    prediction_result = None
    
    if request.method == 'POST':
        try:
            # Extract features from form
            features = [
                float(request.form.get('packet_size')),
                float(request.form.get('inter_arrival')),
                float(request.form.get('packet_rate')),
                float(request.form.get('duration')),
                float(request.form.get('failed_logins'))
            ]
            
            # Make prediction
            result = ml_service.predict(features)
            
            # Calculate threat level
            threat_level = ml_service.calculate_threat_level(
                result['prediction'], 
                result['confidence']
            )
            
            # Save to database
            detection = DetectionHistory(
                user_id=current_user.id,
                packet_size=features[0],
                inter_arrival=features[1],
                packet_rate=features[2],
                duration=features[3],
                failed_logins=features[4],
                prediction=result['prediction'],
                confidence=result['confidence'],
                threat_level=threat_level,
                model_version=result['model_used'],
                ip_address=get_client_ip(request)
            )
            db.session.add(detection)
            db.session.commit()
            
            # Create alert if threat detected and high confidence
            if result['prediction'] == 'Threat' and result['confidence'] >= 0.6:
                alert = Alert(
                    detection_id=detection.id,
                    severity=threat_level
                )
                db.session.add(alert)
                db.session.commit()
            
            # Log detection action
            audit = AuditLog(
                user_id=current_user.id,
                action='detection',
                details={
                    'prediction': result['prediction'],
                    'confidence': result['confidence'],
                    'threat_level': threat_level
                },
                ip_address=get_client_ip(request)
            )
            db.session.add(audit)
            db.session.commit()
            
            prediction_result = {
                **result,
                'threat_level': threat_level,
                'detection_id': detection.id
            }
            
            flash(f'Detection completed: {result["prediction"]} (Confidence: {result["confidence"]:.2%})', 
                  'success' if result['prediction'] == 'Normal' else 'warning')
                  
        except Exception as e:
            flash(f'Error during detection: {str(e)}', 'danger')
    
    return render_template('detection/detect.html', prediction=prediction_result)


@detection_bp.route('/history')
@login_required
def history():
    """Detection history page with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filter options
    prediction_filter = request.args.get('prediction')
    threat_level_filter = request.args.get('threat_level')
    
    query = DetectionHistory.query
    
    # Apply filters
    if prediction_filter:
        query = query.filter_by(prediction=prediction_filter)
    if threat_level_filter:
        query = query.filter_by(threat_level=threat_level_filter)
    
    # Order by most recent first
    query = query.order_by(DetectionHistory.timestamp.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    detections = pagination.items
    
    return render_template('detection/history.html',
                         detections=detections,
                         pagination=pagination,
                         prediction_filter=prediction_filter,
                         threat_level_filter=threat_level_filter)


@detection_bp.route('/batch', methods=['GET', 'POST'])
@login_required
@analyst_required
def batch_detect():
    """Batch detection from CSV upload."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        # TODO: Implement batch processing
        flash('Batch processing feature coming soon!', 'info')
        return redirect(request.url)
    
    return render_template('detection/batch.html')
