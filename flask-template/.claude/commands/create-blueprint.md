---
description: Generate new API blueprint with routes
argument-hint: "<blueprint_name>"
---

Create a new Flask blueprint with basic CRUD structure.

## Arguments

- `blueprint_name` (required): Name of the blueprint (e.g., 'posts', 'comments')

## What Gets Created

1. Blueprint file in `app/api/` with CRUD endpoints
2. Marshmallow schema in `app/schemas/`
3. Model file in `app/models/` (optional)
4. Service file in `app/services/` (optional)

## Example

```bash
# Create posts blueprint
/create-blueprint posts
```

This generates:
- `app/api/posts.py` with GET, POST, PUT, DELETE endpoints
- `app/schemas/post.py` with serialization schemas
- Registers blueprint in `app/api/__init__.py`

## Generated Endpoints

- `GET /api/{blueprint}` - List all resources
- `GET /api/{blueprint}/<id>` - Get single resource
- `POST /api/{blueprint}` - Create new resource
- `PUT /api/{blueprint}/<id>` - Update resource
- `DELETE /api/{blueprint}/<id>` - Delete resource

## Notes

- Blueprint follows RESTful conventions
- All endpoints protected with JWT by default
- Includes pagination for list endpoint
- Uses Marshmallow for validation
- Follows project structure patterns

Provide the blueprint name as $1 argument.
