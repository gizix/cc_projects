---
description: Generate complete REST API endpoints with CRUD operations, following RESTful conventions with proper status codes, error handling, and documentation
allowed-tools: [Read, Write, Grep]
---

This skill provides templates and patterns for generating complete RESTful API endpoints following best practices.

## When This Skill Activates

Automatically activates when:
- Creating new REST API endpoints
- Implementing CRUD operations
- Designing RESTful resources
- Building API modules

## RESTful Endpoint Template

### Complete CRUD Implementation

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models.resource import Resource
from app.schemas.resource import ResourceSchema, ResourceCreateSchema, ResourceUpdateSchema

resource_bp = Blueprint('resources', __name__)

# Initialize schemas
resource_schema = ResourceSchema()
resources_schema = ResourceSchema(many=True)
resource_create_schema = ResourceCreateSchema()
resource_update_schema = ResourceUpdateSchema()


# Collection Endpoints

@resource_bp.route('', methods=['GET'])
@jwt_required()
def list_resources():
    """
    List all resources with pagination.

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)
        sort (str): Sort field
        order (str): Sort order ('asc' or 'desc')
        filter (str): Filter expression

    Returns:
        200: Paginated list of resources
        401: Unauthorized
    """
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # Sorting
    sort_field = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')

    # Build query
    query = Resource.query

    # Apply sorting
    if hasattr(Resource, sort_field):
        order_by = getattr(Resource, sort_field)
        if sort_order == 'desc':
            order_by = order_by.desc()
        query = query.order_by(order_by)

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'resources': resources_schema.dump(pagination.items),
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200


@resource_bp.route('', methods=['POST'])
@jwt_required()
def create_resource():
    """
    Create a new resource.

    Request Body:
        (Schema-defined fields)

    Returns:
        201: Resource created successfully
        400: Validation error
        401: Unauthorized
    """
    try:
        data = resource_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    try:
        resource = Resource(**data, user_id=get_jwt_identity())
        db.session.add(resource)
        db.session.commit()

        return jsonify(resource_schema.dump(resource)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Creation failed', 'message': str(e)}), 500


# Resource Endpoints

@resource_bp.route('/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_resource(resource_id):
    """
    Get a specific resource by ID.

    Args:
        resource_id (int): Resource ID

    Returns:
        200: Resource data
        401: Unauthorized
        404: Resource not found
    """
    resource = Resource.query.get(resource_id)

    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    return jsonify(resource_schema.dump(resource)), 200


@resource_bp.route('/<int:resource_id>', methods=['PUT'])
@jwt_required()
def replace_resource(resource_id):
    """
    Replace a resource (full update).

    Args:
        resource_id (int): Resource ID

    Request Body:
        All required fields

    Returns:
        200: Resource updated
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Resource not found
    """
    resource = Resource.query.get(resource_id)

    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    # Check ownership
    if resource.user_id != get_jwt_identity():
        return jsonify({'error': 'You do not own this resource'}), 403

    try:
        data = resource_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    try:
        for key, value in data.items():
            setattr(resource, key, value)

        db.session.commit()
        return jsonify(resource_schema.dump(resource)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed', 'message': str(e)}), 500


@resource_bp.route('/<int:resource_id>', methods=['PATCH'])
@jwt_required()
def update_resource(resource_id):
    """
    Update a resource (partial update).

    Args:
        resource_id (int): Resource ID

    Request Body:
        Optional fields to update

    Returns:
        200: Resource updated
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Resource not found
    """
    resource = Resource.query.get(resource_id)

    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    if resource.user_id != get_jwt_identity():
        return jsonify({'error': 'You do not own this resource'}), 403

    try:
        data = resource_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    try:
        for key, value in data.items():
            setattr(resource, key, value)

        db.session.commit()
        return jsonify(resource_schema.dump(resource)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed', 'message': str(e)}), 500


@resource_bp.route('/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_resource(resource_id):
    """
    Delete a resource.

    Args:
        resource_id (int): Resource ID

    Returns:
        204: Resource deleted
        401: Unauthorized
        403: Forbidden
        404: Resource not found
    """
    resource = Resource.query.get(resource_id)

    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    if resource.user_id != get_jwt_identity():
        return jsonify({'error': 'You do not own this resource'}), 403

    try:
        db.session.delete(resource)
        db.session.commit()
        return '', 204

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Deletion failed', 'message': str(e)}), 500
```

## HTTP Status Codes Reference

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation error
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

## RESTful URL Conventions

- GET /resources - List all resources
- POST /resources - Create new resource
- GET /resources/:id - Get single resource
- PUT /resources/:id - Replace resource
- PATCH /resources/:id - Update resource
- DELETE /resources/:id - Delete resource

## Nested Resources

```python
# GET /users/:user_id/posts
@users_bp.route('/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    return jsonify([post.to_dict() for post in posts])

# POST /users/:user_id/posts
@users_bp.route('/<int:user_id>/posts', methods=['POST'])
@jwt_required()
def create_user_post(user_id):
    if get_jwt_identity() != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    post = Post(**data, user_id=user_id)
    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_dict()), 201
```

This skill ensures your REST APIs follow industry standards and best practices.
