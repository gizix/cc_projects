"""
Tests for database models.
"""

import pytest
from app.models.user import User


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self, session):
        """Test creating a new user."""
        user = User(
            username='newuser',
            email='newuser@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.is_active is True
        assert user.created_at is not None

    def test_password_hashing(self, session):
        """Test that password is hashed."""
        user = User(
            username='hashtest',
            email='hash@example.com',
            password='plainpassword'
        )
        session.add(user)
        session.commit()

        assert user.password_hash != 'plainpassword'
        assert user.password_hash is not None

    def test_password_verification(self, sample_user):
        """Test password checking."""
        assert sample_user.check_password('TestPassword123!') is True
        assert sample_user.check_password('wrongpassword') is False

    def test_password_not_readable(self, sample_user):
        """Test that password attribute cannot be read."""
        with pytest.raises(AttributeError):
            _ = sample_user.password

    def test_user_to_dict(self, sample_user):
        """Test user serialization to dictionary."""
        user_dict = sample_user.to_dict()

        assert 'id' in user_dict
        assert 'username' in user_dict
        assert 'email' in user_dict
        assert 'is_active' in user_dict
        assert 'created_at' in user_dict
        assert 'password' not in user_dict
        assert 'password_hash' not in user_dict

    def test_user_repr(self, sample_user):
        """Test user string representation."""
        assert repr(sample_user) == '<User testuser>'

    def test_unique_username(self, session, sample_user):
        """Test that username must be unique."""
        from sqlalchemy.exc import IntegrityError

        duplicate_user = User(
            username='testuser',  # Same as sample_user
            email='different@example.com',
            password='password123'
        )
        session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_unique_email(self, session, sample_user):
        """Test that email must be unique."""
        from sqlalchemy.exc import IntegrityError

        duplicate_user = User(
            username='differentuser',
            email='test@example.com',  # Same as sample_user
            password='password123'
        )
        session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            session.commit()
