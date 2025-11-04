"""
User model.

Defines the User model with authentication functionality.
"""

from datetime import datetime
from app.extensions import db, bcrypt


class User(db.Model):
    """User model for authentication and user management."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, username, email, password=None):
        """
        Initialize a new User instance.

        Args:
            username (str): Username
            email (str): Email address
            password (str, optional): Plain text password (will be hashed)
        """
        self.username = username
        self.email = email
        if password:
            self.password = password

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Hash and set the user's password.

        Args:
            password (str): Plain text password
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """
        Check if the provided password matches the user's password.

        Args:
            password (str): Plain text password to check

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        Convert user to dictionary representation.

        Returns:
            dict: User data (excluding password)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of User."""
        return f'<User {self.username}>'
