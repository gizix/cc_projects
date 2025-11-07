"""Application configuration classes.

Environment-specific configurations for Development, Testing, and Production.
Configuration values can be overridden using QUART_ prefixed environment variables.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration with common settings."""

    # Flask/Quart core settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    # JWT Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # CORS
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_DEFAULT = "100/hour"

    # Background Tasks
    BACKGROUND_TASK_SHUTDOWN_TIMEOUT = 30

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class Development(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False

    # More verbose logging in development
    LOG_LEVEL = "DEBUG"

    # Disable rate limiting in development
    RATE_LIMIT_ENABLED = False


class Testing(Config):
    """Testing environment configuration."""

    DEBUG = False
    TESTING = True

    # Use in-memory SQLite for tests
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"

    # Faster token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

    # Disable rate limiting in tests
    RATE_LIMIT_ENABLED = False


class Production(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Require environment variables in production
    SECRET_KEY = os.environ["SECRET_KEY"]
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    DATABASE_URL = os.environ["DATABASE_URL"]

    # Stricter CORS in production
    CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"].split(",")

    # Enable rate limiting
    RATE_LIMIT_ENABLED = True


# Configuration dictionary for easy access
config = {
    "development": Development,
    "testing": Testing,
    "production": Production,
    "default": Development,
}
