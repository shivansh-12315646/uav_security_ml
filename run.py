"""
Development entry point for running the Flask application.
For production, use wsgi.py with Gunicorn.
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
