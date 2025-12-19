"""
Primary Development Entry Point for UAV Security ML System
===========================================================

This is the MAIN ENTRY POINT for running the full-featured Flask application.
Use this instead of app.py for production or full-featured development.

Features available through this entry point:
- Complete user authentication and authorization
- Database persistence for all data
- Alert system with severity levels
- Advanced analytics dashboard
- Admin panel for user management
- RESTful API endpoints
- CSRF protection for forms
- Real-time updates via WebSocket
- Background task processing
- Rate limiting and security features

For production deployment, use wsgi.py with Gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

For a simplified demo version without authentication/database,
see app.py (not recommended for production use).

Usage:
    python run.py
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run with standard Flask
    # Debug mode controlled by FLASK_ENV environment variable
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
