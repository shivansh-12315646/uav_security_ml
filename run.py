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
    # Run with standard Flask (SocketIO disabled for now)
    app.run(debug=True, host='0.0.0.0', port=5000)
