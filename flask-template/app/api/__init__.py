"""
API package.

Contains all API blueprints.
"""

from app.api.auth import auth_bp
from app.api.users import users_bp
from app.api.resources import resources_bp

__all__ = ['auth_bp', 'users_bp', 'resources_bp']
