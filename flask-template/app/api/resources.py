"""
Resources API endpoints.

Example blueprint for additional resources.
You can use this as a template for creating new API endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

resources_bp = Blueprint('resources', __name__)


@resources_bp.route('', methods=['GET'])
@jwt_required()
def get_resources():
    """
    Get all resources.

    This is a placeholder endpoint. Replace with your actual resource logic.

    Returns:
        200: List of resources
        401: Not authenticated
    """
    # Example response
    resources = [
        {'id': 1, 'name': 'Resource 1', 'description': 'Example resource'},
        {'id': 2, 'name': 'Resource 2', 'description': 'Another example'}
    ]

    return jsonify({'resources': resources}), 200


@resources_bp.route('/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_resource(resource_id):
    """
    Get a specific resource by ID.

    Args:
        resource_id (int): Resource ID

    Returns:
        200: Resource data
        401: Not authenticated
        404: Resource not found
    """
    # Example response
    resource = {'id': resource_id, 'name': f'Resource {resource_id}', 'description': 'Example resource'}

    return jsonify(resource), 200


@resources_bp.route('', methods=['POST'])
@jwt_required()
def create_resource():
    """
    Create a new resource.

    Request Body:
        name (str): Resource name
        description (str): Resource description

    Returns:
        201: Resource created successfully
        400: Validation error
        401: Not authenticated
    """
    data = request.json

    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    # Example response
    resource = {
        'id': 3,
        'name': data['name'],
        'description': data.get('description', '')
    }

    return jsonify({'message': 'Resource created successfully', 'resource': resource}), 201


@resources_bp.route('/<int:resource_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_resource(resource_id):
    """
    Update a resource.

    Args:
        resource_id (int): Resource ID

    Request Body:
        name (str, optional): New name
        description (str, optional): New description

    Returns:
        200: Resource updated successfully
        401: Not authenticated
        404: Resource not found
    """
    data = request.json

    # Example response
    resource = {
        'id': resource_id,
        'name': data.get('name', f'Resource {resource_id}'),
        'description': data.get('description', 'Updated resource')
    }

    return jsonify({'message': 'Resource updated successfully', 'resource': resource}), 200


@resources_bp.route('/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_resource(resource_id):
    """
    Delete a resource.

    Args:
        resource_id (int): Resource ID

    Returns:
        200: Resource deleted successfully
        401: Not authenticated
        404: Resource not found
    """
    return jsonify({'message': 'Resource deleted successfully'}), 200
