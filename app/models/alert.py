"""Alert model for managing security alerts."""
from datetime import datetime
from app.extensions import db


class Alert(db.Model):
    """Model for security alerts generated from threat detections."""
    
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detection_history.id'), nullable=False, index=True)
    
    # Alert Details
    severity = db.Column(db.String(20), nullable=False)  # 'Low', 'Medium', 'High', 'Critical'
    status = db.Column(db.String(20), default='Open', nullable=False)  # 'Open', 'Acknowledged', 'Resolved', 'False Positive'
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # Resolution
    resolution_notes = db.Column(db.Text)
    
    def __init__(self, detection_id, severity, assigned_to=None):
        """Initialize alert."""
        self.detection_id = detection_id
        self.severity = severity
        self.assigned_to = assigned_to
    
    def acknowledge(self, user_id=None):
        """Mark alert as acknowledged."""
        self.status = 'Acknowledged'
        self.acknowledged_at = datetime.utcnow()
        if user_id:
            self.assigned_to = user_id
        db.session.commit()
    
    def resolve(self, notes=None):
        """Mark alert as resolved."""
        self.status = 'Resolved'
        self.resolved_at = datetime.utcnow()
        if notes:
            self.resolution_notes = notes
        db.session.commit()
    
    def mark_false_positive(self, notes=None):
        """Mark alert as false positive."""
        self.status = 'False Positive'
        self.resolved_at = datetime.utcnow()
        if notes:
            self.resolution_notes = notes
        db.session.commit()
    
    def __repr__(self):
        return f'<Alert {self.id}: {self.severity} - {self.status}>'
    
    def to_dict(self):
        """Convert alert to dictionary."""
        return {
            'id': self.id,
            'detection_id': self.detection_id,
            'severity': self.severity,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes
        }
