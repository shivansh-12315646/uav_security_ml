"""Audit log model for tracking user actions."""
from datetime import datetime
from app.extensions import db
import json


class AuditLog(db.Model):
    """Model for auditing user actions."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Action Details
    action = db.Column(db.String(100), nullable=False)  # 'login', 'detection', 'model_update', etc.
    details = db.Column(db.Text)  # JSON string with additional details
    
    # Request Information
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, user_id, action, details=None, ip_address=None, user_agent=None):
        """Initialize audit log entry."""
        self.user_id = user_id
        self.action = action
        self.details = json.dumps(details) if details and isinstance(details, dict) else details
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def get_details(self):
        """Parse and return details as dictionary."""
        if self.details:
            try:
                return json.loads(self.details)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} by user {self.user_id}>'
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.get_details(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
