"""
WSGI entry point for production deployment.

This file is used by WSGI servers (Gunicorn, uWSGI, etc.) to run the application.
"""

from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # For development only - use flask run or gunicorn in production
    app.run()
