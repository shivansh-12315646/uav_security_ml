"""
Flask application factory.
Creates and configures the Flask application with all extensions and blueprints.
"""
import os
from flask import Flask, render_template
from config import config
from app.extensions import init_extensions, db, socketio


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration name ('development', 'testing', 'production')
    
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize ML service
    from app.services.ml_service import ml_service
    ml_service.init_app(app)
    
    # Initialize training service
    from app.services.training_service import training_service
    training_service.init_app(app, socketio)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_default_admin()
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.detection import detection_bp
    from app.routes.analytics import analytics_bp
    from app.routes.alerts import alerts_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.settings import settings_bp
    from app.routes.training import training_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(training_bp)


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def register_commands(app):
    """Register Flask CLI commands."""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized.")
    
    @app.cli.command()
    def create_admin():
        """Create an admin user."""
        from app.models.user import User
        
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@uavsecurity.com')
        password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if User.query.filter_by(username=username).first():
            print(f"Admin user '{username}' already exists.")
            return
        
        admin = User(username=username, email=email, password=password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")


def create_default_admin():
    """Create default admin user if it doesn't exist."""
    from app.models.user import User
    
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@uavsecurity.com')
    password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    if not User.query.filter_by(username=username).first():
        admin = User(username=username, email=email, password=password, role='admin')
        db.session.add(admin)
        db.session.commit()


# Export socketio for use in run.py
__all__ = ['create_app', 'socketio']
