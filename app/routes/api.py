"""RESTful API routes."""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db, limiter
from app.models.detection import DetectionHistory
from app.models.alert import Alert
from app.services.ml_service import ml_service

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/detect', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def api_detect():
    """API endpoint for single detection."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['packet_size', 'inter_arrival', 'packet_rate', 'duration', 'failed_logins']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        features = [
            float(data['packet_size']),
            float(data['inter_arrival']),
            float(data['packet_rate']),
            float(data['duration']),
            float(data['failed_logins'])
        ]
        
        result = ml_service.predict(features)
        threat_level = ml_service.calculate_threat_level(result['prediction'], result['confidence'])
        
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
            model_version=result['model_used']
        )
        db.session.add(detection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'detection_id': detection.id,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'threat_level': threat_level,
            'model_used': result['model_used']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/history', methods=['GET'])
@login_required
def api_history():
    """API endpoint for detection history."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = DetectionHistory.query.order_by(DetectionHistory.timestamp.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'detections': [d.to_dict() for d in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })


@api_bp.route('/alerts', methods=['GET'])
@login_required
def api_alerts():
    """API endpoint for alerts."""
    status = request.args.get('status', 'Open')
    
    query = Alert.query
    if status != 'All':
        query = query.filter_by(status=status)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(50).all()
    
    return jsonify({
        'alerts': [a.to_dict() for a in alerts]
    })


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'UAV Security ML',
        'version': '2.0.0'
    })
