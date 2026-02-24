"""Django ORM models for UAV Security ML system."""
import json
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='viewer'):
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        user = self.model(username=username, email=self.normalize_email(email), role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password, role='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [('admin', 'Admin'), ('analyst', 'Analyst'), ('viewer', 'Viewer')]

    username = models.CharField(max_length=80, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_login_at = models.DateTimeField(null=True, blank=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'

    def is_admin(self):
        return self.role == 'admin'

    def is_analyst_role(self):
        return self.role == 'analyst'

    def can_access(self, required_role):
        hierarchy = {'admin': 3, 'analyst': 2, 'viewer': 1}
        return hierarchy.get(self.role, 0) >= hierarchy.get(required_role, 0)

    def update_last_login(self):
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login_at.isoformat() if self.last_login_at else None,
        }

    def __str__(self):
        return self.username


class DetectionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detections', db_index=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    altitude = models.FloatField()
    speed = models.FloatField()
    direction = models.FloatField()
    signal_strength = models.FloatField()
    distance_from_base = models.FloatField()
    flight_time = models.FloatField()
    battery_level = models.FloatField()
    temperature = models.FloatField()
    vibration = models.FloatField()
    gps_accuracy = models.FloatField()

    prediction = models.CharField(max_length=50)
    confidence = models.FloatField()
    threat_level = models.CharField(max_length=20, blank=True, null=True)
    model_version = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'detection_history'
        ordering = ['-timestamp']

    def __str__(self):
        return f'Detection {self.id}: {self.prediction} ({self.confidence:.2f})'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'altitude': self.altitude,
            'speed': self.speed,
            'direction': self.direction,
            'signal_strength': self.signal_strength,
            'distance_from_base': self.distance_from_base,
            'flight_time': self.flight_time,
            'battery_level': self.battery_level,
            'temperature': self.temperature,
            'vibration': self.vibration,
            'gps_accuracy': self.gps_accuracy,
            'prediction': self.prediction,
            'confidence': round(self.confidence, 4),
            'threat_level': self.threat_level,
            'model_version': self.model_version,
            'ip_address': self.ip_address,
            'notes': self.notes,
        }


class Alert(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'), ('Acknowledged', 'Acknowledged'),
        ('Resolved', 'Resolved'), ('False Positive', 'False Positive'),
    ]

    detection = models.ForeignKey(DetectionHistory, on_delete=models.CASCADE, related_name='alerts', db_index=True)
    severity = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_alerts')
    created_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']

    def acknowledge(self, user_id=None):
        self.status = 'Acknowledged'
        self.acknowledged_at = timezone.now()
        if user_id:
            self.assigned_to_id = user_id
        self.save()

    def resolve(self, notes=None):
        self.status = 'Resolved'
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save()

    def mark_false_positive(self, notes=None):
        self.status = 'False Positive'
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save()

    def to_dict(self):
        return {
            'id': self.id,
            'detection_id': self.detection_id,
            'severity': self.severity,
            'status': self.status,
            'assigned_to': self.assigned_to_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes,
        }

    def __str__(self):
        return f'Alert {self.id}: {self.severity} - {self.status}'


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs', db_index=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

    def __init__(self, *args, details=None, **kwargs):
        if isinstance(details, dict):
            details = json.dumps(details)
        super().__init__(*args, details=details, **kwargs)

    def get_details(self):
        if self.details:
            try:
                return json.loads(self.details)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.get_details(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

    def __str__(self):
        return f'AuditLog {self.id}: {self.action} by {self.user_id}'


class MLModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    trained_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trained_models')
    training_dataset_size = models.IntegerField(null=True, blank=True)
    training_duration = models.FloatField(null=True, blank=True)
    hyperparameters = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ml_models'
        ordering = ['-created_at']

    def activate(self):
        MLModel.objects.filter(name=self.name, is_active=True).update(is_active=False)
        self.is_active = True
        self.save()

    def to_dict(self):
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
            'trained_by': self.trained_by_id,
            'training_dataset_size': self.training_dataset_size,
            'training_duration': self.training_duration,
            'description': self.description,
        }

    def __str__(self):
        return f'{self.name} v{self.version}'
