---
description: Generate new route blueprint
argument-hint: <route_name>
allowed-tools: Read, Write, Grep
model: sonnet
---

Create a new route blueprint with boilerplate async route handlers, Pydantic schemas, and quart-schema integration.

## Arguments

- `$1`: Route name (e.g., "posts", "comments", "products")

## Usage

```bash
/create-route posts
/create-route comments
/create-route products
```

## What This Creates

1. **Route Blueprint** (`src/app/routes/{name}.py`):
   - Blueprint definition
   - CRUD endpoint stubs (GET, POST, PUT, DELETE)
   - Async route handlers
   - JWT protection decorators
   - quart-schema validation

2. **Pydantic Schemas** (`src/app/schemas/{name}.py`):
   - Request validation schemas
   - Response serialization schemas
   - Example fields with types

3. **Blueprint Registration**:
   - Updates `src/app/__init__.py` to register blueprint

## Generated Route Example

```python
from quart import Blueprint, jsonify
from quart_schema import validate_request, validate_response
from quart_jwt_extended import jwt_required

{name}_bp = Blueprint('{name}', __name__, url_prefix='/api/{name}')

@{name}_bp.get('/')
@jwt_required
@validate_response({Name}ListResponse)
async def list_{name}() -> tuple:
    # TODO: Implement list logic
    return {Name}ListResponse(items=[]), 200

@{name}_bp.post('/')
@jwt_required
@validate_request({Name}CreateRequest)
@validate_response({Name}Response)
async def create_{name}(data: {Name}CreateRequest) -> tuple:
    # TODO: Implement create logic
    return {Name}Response(...), 201
```

## Generated Schema Example

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class {Name}CreateRequest:
    title: str
    description: Optional[str] = None

@dataclass
class {Name}Response:
    id: int
    title: str
    description: Optional[str]
    created_at: str
```

## Next Steps After Generation

1. Implement database operations in route handlers
2. Add business logic
3. Create corresponding model with `/create-model`
4. Write tests for endpoints
5. Customize schemas for your needs

## Notes

- Routes follow REST conventions
- All handlers are async
- JWT authentication included
- Validation with quart-schema
- Auto-generates OpenAPI docs
