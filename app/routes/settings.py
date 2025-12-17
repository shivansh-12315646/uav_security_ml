"""Settings routes."""
from flask import Blueprint, render_template
from flask_login import login_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def settings():
    """User settings page."""
    return render_template('auth/profile.html')
