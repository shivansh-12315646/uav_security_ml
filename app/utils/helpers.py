"""Helper utility functions."""
import os
from datetime import datetime, timedelta
from flask import current_app
import hashlib


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string."""
    if dt is None:
        return ''
    return dt.strftime(format)


def get_time_ago(dt):
    """Get human-readable time ago string."""
    if dt is None:
        return 'Never'
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'Just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif seconds < 2592000:  # 30 days
        days = int(seconds / 86400)
        return f'{days} day{"s" if days != 1 else ""} ago'
    else:
        months = int(seconds / 2592000)
        return f'{months} month{"s" if months != 1 else ""} ago'


def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values."""
    if previous == 0:
        return 0 if current == 0 else 100
    return ((current - previous) / previous) * 100


def ensure_dir_exists(directory):
    """Ensure directory exists, create if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_client_ip(request):
    """Get client IP address from request."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr or 'Unknown'
