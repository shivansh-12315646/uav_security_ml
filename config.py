"""
Configuration classes for different environments.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Basic Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///uav_security.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'uav_session:'
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Security
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 10))
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@uavsecurity.com')
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # ML Models
    ML_MODELS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models', 'saved_models')
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'RandomForest')
    MODEL_CONFIDENCE_THRESHOLD = float(os.getenv('MODEL_CONFIDENCE_THRESHOLD', 0.7))
    
    # Pagination
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
    
    # Notifications
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'False') == 'True'
    ENABLE_SLACK_NOTIFICATIONS = os.getenv('ENABLE_SLACK_NOTIFICATIONS', 'False') == 'True'
    
    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # CORS
    CORS_HEADERS = 'Content-Type'
    
    # SocketIO
    SOCKETIO_MESSAGE_QUEUE = os.getenv('REDIS_URL', 'redis://localhost:6379/0')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    BCRYPT_LOG_ROUNDS = 4  # Faster for testing


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # Override with production values
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True


# Config dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
