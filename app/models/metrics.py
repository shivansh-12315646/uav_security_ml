"""System metrics model for monitoring application health."""
from datetime import datetime
from app.extensions import db


class SystemMetrics(db.Model):
    """Model for storing system performance metrics."""
    
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # System Resources
    cpu_usage = db.Column(db.Float)  # Percentage
    memory_usage = db.Column(db.Float)  # Percentage
    disk_usage = db.Column(db.Float)  # Percentage
    
    # Application Metrics
    active_threats = db.Column(db.Integer, default=0)
    total_detections_today = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float)  # in milliseconds
    active_users = db.Column(db.Integer, default=0)
    
    # Database Metrics
    database_size = db.Column(db.Float)  # in MB
    
    def __init__(self, cpu_usage=None, memory_usage=None, disk_usage=None,
                 active_threats=0, total_detections_today=0, avg_response_time=None,
                 active_users=0, database_size=None):
        """Initialize system metrics record."""
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.disk_usage = disk_usage
        self.active_threats = active_threats
        self.total_detections_today = total_detections_today
        self.avg_response_time = avg_response_time
        self.active_users = active_users
        self.database_size = database_size
    
    def __repr__(self):
        return f'<SystemMetrics {self.timestamp}: CPU {self.cpu_usage}%>'
    
    def to_dict(self):
        """Convert metrics to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'cpu_usage': round(self.cpu_usage, 2) if self.cpu_usage else None,
            'memory_usage': round(self.memory_usage, 2) if self.memory_usage else None,
            'disk_usage': round(self.disk_usage, 2) if self.disk_usage else None,
            'active_threats': self.active_threats,
            'total_detections_today': self.total_detections_today,
            'avg_response_time': round(self.avg_response_time, 2) if self.avg_response_time else None,
            'active_users': self.active_users,
            'database_size': round(self.database_size, 2) if self.database_size else None
        }
