"""
User schemas.

Marshmallow schemas for User model serialization and validation.
"""

from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma
from app.models.user import User
import re


class UserSchema(ma.SQLAlchemySchema):
    """Schema for serializing User model (read operations)."""

    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field()
    email = ma.auto_field()
    is_active = ma.auto_field()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserCreateSchema(ma.Schema):
    """Schema for creating a new user."""

    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        load_only=True
    )

    @validates('username')
    def validate_username(self, value):
        """Validate that username contains only alphanumeric characters and underscores."""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username must contain only letters, numbers, and underscores')

        # Check if username already exists
        if User.query.filter_by(username=value).first():
            raise ValidationError('Username already exists')

    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already registered."""
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')


class UserUpdateSchema(ma.Schema):
    """Schema for updating a user."""

    username = fields.String(validate=validate.Length(min=3, max=80))
    email = fields.Email()
    is_active = fields.Boolean()
    password = fields.String(
        validate=validate.Length(min=8),
        load_only=True
    )

    @validates('username')
    def validate_username(self, value):
        """Validate that username contains only alphanumeric characters and underscores."""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username must contain only letters, numbers, and underscores')


class LoginSchema(ma.Schema):
    """Schema for user login."""

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class TokenSchema(ma.Schema):
    """Schema for token response."""

    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(default='bearer')
