"""
Flask extensions initialization.
Centralized location for all Flask extensions.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_session import Session

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
cors = CORS()
csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*")
sess = Session()


def init_extensions(app):
    """Initialize Flask extensions with app instance."""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cors.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app, message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'))
    sess.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
