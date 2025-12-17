"""
WSGI entry point for production deployment with Gunicorn.
Usage: gunicorn wsgi:app
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run()
