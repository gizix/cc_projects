"""
Custom decorators for Flask routes.

Provides reusable decorators for common authentication and authorization patterns.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def admin_required():
    """
    Decorator to require admin privileges.

    Note: This is a placeholder. Implement actual role-based access control
    by adding a 'role' field to the User model.

    Usage:
        @app.route('/admin/users')
        @jwt_required()
        @admin_required()
        def admin_users():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # TODO: Implement actual admin check
            # Example: if not user.is_admin:
            #     return jsonify({'error': 'Admin access required'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission):
    """
    Decorator to require specific permission.

    Args:
        permission (str): Required permission name

    Usage:
        @app.route('/posts/<id>/edit')
        @jwt_required()
        @permission_required('edit_posts')
        def edit_post(id):
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # TODO: Implement permission checking
            # Example: if not user.has_permission(permission):
            #     return jsonify({'error': f'Permission denied: {permission}'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def resource_owner_required(get_resource_fn, owner_field='user_id'):
    """
    Decorator to require that current user owns the resource.

    Args:
        get_resource_fn (callable): Function to get the resource (receives kwargs)
        owner_field (str): Field name containing the owner's user ID

    Usage:
        def get_post(post_id):
            return Post.query.get_or_404(post_id)

        @app.route('/posts/<int:post_id>/edit')
        @jwt_required()
        @resource_owner_required(lambda **kw: get_post(kw['post_id']))
        def edit_post(post_id):
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            resource = get_resource_fn(**kwargs)

            if not resource:
                return jsonify({'error': 'Resource not found'}), 404

            resource_owner_id = getattr(resource, owner_field, None)

            if resource_owner_id != current_user_id:
                return jsonify({'error': 'You do not own this resource'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
