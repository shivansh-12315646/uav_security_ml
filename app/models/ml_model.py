"""ML Model metadata model for tracking model versions."""
from datetime import datetime
from app.extensions import db


class MLModel(db.Model):
    """Model for tracking ML model versions and performance."""
    
    __tablename__ = 'ml_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 'RandomForest', 'XGBoost', etc.
    version = db.Column(db.String(50), nullable=False)
    
    # Performance Metrics
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    
    # Model Status
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    trained_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Additional Information
    training_dataset_size = db.Column(db.Integer)
    training_duration = db.Column(db.Float)  # in seconds
    hyperparameters = db.Column(db.Text)  # JSON string
    description = db.Column(db.Text)
    
    def __init__(self, name, version, file_path, accuracy=None, precision=None,
                 recall=None, f1_score=None, trained_by=None, is_active=False):
        """Initialize ML model record."""
        self.name = name
        self.version = version
        self.file_path = file_path
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1_score = f1_score
        self.trained_by = trained_by
        self.is_active = is_active
    
    def activate(self):
        """Activate this model and deactivate others of same type."""
        # Deactivate all other models of the same type
        MLModel.query.filter_by(name=self.name, is_active=True).update({'is_active': False})
        self.is_active = True
        db.session.commit()
    
    def __repr__(self):
        return f'<MLModel {self.name} v{self.version}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'accuracy': round(self.accuracy, 4) if self.accuracy else None,
            'precision': round(self.precision, 4) if self.precision else None,
            'recall': round(self.recall, 4) if self.recall else None,
            'f1_score': round(self.f1_score, 4) if self.f1_score else None,
            'is_active': self.is_active,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'trained_by': self.trained_by,
            'training_dataset_size': self.training_dataset_size,
            'training_duration': self.training_duration,
            'description': self.description
        }
