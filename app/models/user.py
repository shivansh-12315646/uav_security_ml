"""User model for authentication and authorization."""
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """User model with role-based access control."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # admin, analyst, viewer
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    profile_image = db.Column(db.String(255))
    
    # Relationships
    detections = db.relationship('DetectionHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    trained_models = db.relationship('MLModel', backref='trainer', lazy='dynamic', foreign_keys='MLModel.trained_by')
    assigned_alerts = db.relationship('Alert', backref='assigned_user', lazy='dynamic', foreign_keys='Alert.assigned_to')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, role='viewer'):
        """Initialize user with hashed password."""
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_analyst(self):
        """Check if user has analyst role."""
        return self.role == 'analyst'
    
    def can_access(self, required_role):
        """Check if user can access resource based on role hierarchy."""
        role_hierarchy = {'admin': 3, 'analyst': 2, 'viewer': 1}
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_image': self.profile_image
        }
