"""Detection history model for storing UAV threat predictions."""
from datetime import datetime
from app.extensions import db


class DetectionHistory(db.Model):
    """Model for storing UAV detection results."""
    
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # UAV Features
    packet_size = db.Column(db.Float, nullable=False)
    inter_arrival = db.Column(db.Float, nullable=False)
    packet_rate = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    failed_logins = db.Column(db.Float, nullable=False)
    
    # Prediction Results
    prediction = db.Column(db.String(20), nullable=False)  # 'Normal' or 'Threat'
    confidence = db.Column(db.Float, nullable=False)  # 0-1
    threat_level = db.Column(db.String(20))  # 'Low', 'Medium', 'High', 'Critical'
    model_version = db.Column(db.String(50))
    
    # Additional Information
    ip_address = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # Relationships
    alerts = db.relationship('Alert', backref='detection', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, packet_size, inter_arrival, packet_rate, 
                 duration, failed_logins, prediction, confidence, 
                 threat_level=None, model_version=None, ip_address=None, notes=None):
        """Initialize detection record."""
        self.user_id = user_id
        self.packet_size = packet_size
        self.inter_arrival = inter_arrival
        self.packet_rate = packet_rate
        self.duration = duration
        self.failed_logins = failed_logins
        self.prediction = prediction
        self.confidence = confidence
        self.threat_level = threat_level or self._calculate_threat_level(confidence)
        self.model_version = model_version
        self.ip_address = ip_address
        self.notes = notes
    
    def _calculate_threat_level(self, confidence):
        """Calculate threat level based on confidence score."""
        if self.prediction == 'Normal':
            return 'Low'
        
        if confidence >= 0.9:
            return 'Critical'
        elif confidence >= 0.75:
            return 'High'
        elif confidence >= 0.6:
            return 'Medium'
        else:
            return 'Low'
    
    def __repr__(self):
        return f'<Detection {self.id}: {self.prediction} ({self.confidence:.2f})>'
    
    def to_dict(self):
        """Convert detection to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'packet_size': self.packet_size,
            'inter_arrival': self.inter_arrival,
            'packet_rate': self.packet_rate,
            'duration': self.duration,
            'failed_logins': self.failed_logins,
            'prediction': self.prediction,
            'confidence': round(self.confidence, 4),
            'threat_level': self.threat_level,
            'model_version': self.model_version,
            'ip_address': self.ip_address,
            'notes': self.notes
        }
