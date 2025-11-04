"""
Application configuration.

Defines configuration classes for different environments.
"""

import os
from datetime import timedelta
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).parent.parent


class Config:
    """Base configuration with default settings."""

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'

    # SQLAlchemy Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False

    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "instance" / "dev.db"}'

    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries in console


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG = False
    TESTING = True

    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4

    # Shorter JWT expiration for tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Production database (PostgreSQL recommended)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Validate required environment variables
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")

    if not os.environ.get('JWT_SECRET_KEY'):
        raise ValueError("JWT_SECRET_KEY environment variable must be set in production")

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")

    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CORS - restrict origins in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
