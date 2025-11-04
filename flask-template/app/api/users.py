"""
Users API endpoints.

Handles user CRUD operations.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User
from app.schemas.user import UserSchema, UserUpdateSchema

users_bp = Blueprint('users', __name__)

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserUpdateSchema()


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """
    Get all users (paginated).

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)

    Returns:
        200: List of users with pagination info
        401: Not authenticated
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    pagination = User.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'users': users_schema.dump(pagination.items),
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get a specific user by ID.

    Args:
        user_id (int): User ID

    Returns:
        200: User data
        401: Not authenticated
        404: User not found
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user_schema.dump(user)), 200


@users_bp.route('/<int:user_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_user(user_id):
    """
    Update a user.

    Note: Users can only update their own profile unless they have admin privileges.

    Args:
        user_id (int): User ID

    Request Body:
        username (str, optional): New username
        email (str, optional): New email
        password (str, optional): New password
        is_active (bool, optional): Active status

    Returns:
        200: User updated successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized to update this user
        404: User not found
    """
    current_user_id = get_jwt_identity()

    # Check if user is updating their own profile
    if current_user_id != user_id:
        return jsonify({'error': 'You can only update your own profile'}), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        # Validate input
        data = user_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    try:
        # Update user fields
        if 'username' in data:
            # Check if new username is already taken
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Username already taken'}), 400
            user.username = data['username']

        if 'email' in data:
            # Check if new email is already registered
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already registered'}), 400
            user.email = data['email']

        if 'password' in data:
            user.password = data['password']

        if 'is_active' in data:
            user.is_active = data['is_active']

        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': user_schema.dump(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed', 'message': str(e)}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete a user.

    Note: Users can only delete their own account unless they have admin privileges.

    Args:
        user_id (int): User ID

    Returns:
        200: User deleted successfully
        401: Not authenticated
        403: Not authorized to delete this user
        404: User not found
    """
    current_user_id = get_jwt_identity()

    # Check if user is deleting their own account
    if current_user_id != user_id:
        return jsonify({'error': 'You can only delete your own account'}), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Deletion failed', 'message': str(e)}), 500
