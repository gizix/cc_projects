"""
Authentication service.

Handles authentication business logic.
"""

from typing import Optional, Tuple
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app.extensions import db


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def register_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.

        Args:
            username (str): Username
            email (str): Email address
            password (str): Plain text password

        Returns:
            Tuple[Optional[User], Optional[str]]: (user, error_message)
        """
        # Check if username exists
        if User.query.filter_by(username=username).first():
            return None, 'Username already exists'

        # Check if email exists
        if User.query.filter_by(email=email).first():
            return None, 'Email already registered'

        try:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def authenticate_user(email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user with email and password.

        Args:
            email (str): Email address
            password (str): Plain text password

        Returns:
            Tuple[Optional[User], Optional[str]]: (user, error_message)
        """
        user = User.query.filter_by(email=email).first()

        if not user:
            return None, 'Invalid email or password'

        if not user.check_password(password):
            return None, 'Invalid email or password'

        if not user.is_active:
            return None, 'Account is deactivated'

        return user, None

    @staticmethod
    def generate_tokens(user_id: int) -> dict:
        """
        Generate access and refresh tokens for a user.

        Args:
            user_id (int): User ID

        Returns:
            dict: Dictionary containing access_token and refresh_token
        """
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
