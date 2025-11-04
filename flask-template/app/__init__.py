"""
Application factory module.

Creates and configures the Flask application instance.
"""

import os
from flask import Flask
from app.config import config
from app.extensions import db, migrate, jwt, cors, ma, bcrypt


def create_app(config_name=None):
    """
    Application factory function.

    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
                          Defaults to FLASK_ENV environment variable or 'development'

    Returns:
        Flask: Configured Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    ma.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.api import auth_bp, users_bp, resources_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(resources_bp, url_prefix='/api/resources')

    # Register error handlers
    register_error_handlers(app)

    # Register CLI commands
    register_cli_commands(app)

    # Add security headers
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if app.config.get('SESSION_COOKIE_SECURE'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Simple health check endpoint."""
        return {'status': 'healthy'}, 200

    return app


def register_error_handlers(app):
    """Register error handlers for the application."""

    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'The requested resource was not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500


def register_cli_commands(app):
    """Register custom CLI commands."""

    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized successfully.')

    @app.cli.command('seed-db')
    def seed_db():
        """Seed the database with sample data."""
        from app.models.user import User

        # Create sample users
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password='password123'
            )
            db.session.add(admin)

        if not User.query.filter_by(email='user@example.com').first():
            user = User(
                username='user',
                email='user@example.com',
                password='password123'
            )
            db.session.add(user)

        db.session.commit()
        print('Database seeded successfully.')
