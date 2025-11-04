"""
Authentication API endpoints.

Handles user registration, login, token refresh, and logout.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User
from app.schemas.user import UserCreateSchema, LoginSchema, UserSchema

auth_bp = Blueprint('auth', __name__)

# Initialize schemas
user_create_schema = UserCreateSchema()
login_schema = LoginSchema()
user_schema = UserSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request Body:
        username (str): Unique username
        email (str): Email address
        password (str): Password (min 8 characters)

    Returns:
        201: User created successfully
        400: Validation error
        500: Server error
    """
    try:
        # Validate and deserialize input
        data = user_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    try:
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.

    Request Body:
        email (str): User's email
        password (str): User's password

    Returns:
        200: Login successful with access and refresh tokens
        400: Validation error
        401: Invalid credentials
    """
    try:
        # Validate input
        data = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    # Find user by email
    user = User.query.filter_by(email=data['email']).first()

    # Verify password
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check if user is active
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401

    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': user_schema.dump(user)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)

    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's information.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: User information
        401: Not authenticated
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user_schema.dump(user)), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should discard tokens).

    Note: JWT is stateless, so actual token invalidation requires a token blacklist.
    For now, this endpoint just confirms logout and client should delete tokens.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Logout successful
    """
    # In a production app, you would add the token to a blacklist here
    # For example, using Redis to store revoked tokens
    jti = get_jwt()['jti']  # JWT ID, unique identifier for the token

    return jsonify({'message': 'Successfully logged out'}), 200
