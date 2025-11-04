"""
User service.

Handles user-related business logic.
"""

from typing import Optional, Dict, Any
from app.models.user import User
from app.extensions import db


class UserService:
    """Service class for user operations."""

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id (int): User ID

        Returns:
            Optional[User]: User object or None
        """
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email (str): Email address

        Returns:
            Optional[User]: User object or None
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username (str): Username

        Returns:
            Optional[User]: User object or None
        """
        return User.query.filter_by(username=username).first()

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> tuple[Optional[User], Optional[str]]:
        """
        Update a user's information.

        Args:
            user_id (int): User ID
            data (dict): Dictionary containing fields to update

        Returns:
            tuple[Optional[User], Optional[str]]: (updated_user, error_message)
        """
        user = User.query.get(user_id)

        if not user:
            return None, 'User not found'

        try:
            # Update username if provided and not taken
            if 'username' in data:
                existing = User.query.filter_by(username=data['username']).first()
                if existing and existing.id != user_id:
                    return None, 'Username already taken'
                user.username = data['username']

            # Update email if provided and not taken
            if 'email' in data:
                existing = User.query.filter_by(email=data['email']).first()
                if existing and existing.id != user_id:
                    return None, 'Email already registered'
                user.email = data['email']

            # Update password if provided
            if 'password' in data:
                user.password = data['password']

            # Update active status if provided
            if 'is_active' in data:
                user.is_active = data['is_active']

            db.session.commit()
            return user, None

        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_user(user_id: int) -> tuple[bool, Optional[str]]:
        """
        Delete a user.

        Args:
            user_id (int): User ID

        Returns:
            tuple[bool, Optional[str]]: (success, error_message)
        """
        user = User.query.get(user_id)

        if not user:
            return False, 'User not found'

        try:
            db.session.delete(user)
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_all_users(page: int = 1, per_page: int = 20):
        """
        Get all users with pagination.

        Args:
            page (int): Page number
            per_page (int): Items per page

        Returns:
            Pagination: Flask-SQLAlchemy pagination object
        """
        return User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
