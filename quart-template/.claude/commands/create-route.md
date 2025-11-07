---
description: Add API endpoint with validation
argument-hint: "<blueprint-name> <method> <path>"
---

Add a new API route to an existing blueprint with Quart-Schema validation.

Arguments:
- $1: Blueprint name (e.g., "api", "auth")
- $2: HTTP method (GET, POST, PUT, DELETE)
- $3: Route path (e.g., "/users/<int:user_id>")

I'll create a new $2 route at "$3" in the $1 blueprint.

Steps I'll take:
1. Open `src/app/routes/$1/__init__.py`
2. Add route handler with async function
3. Add appropriate Quart-Schema decorators:
   - @validate_request for POST/PUT
   - @validate_response for all methods
   - @tag for OpenAPI documentation
4. Add authentication if needed (@require_auth or @optional_auth)
5. Include error handling
6. Create/update Pydantic schemas if needed

Example result:
```python
@$1_bp.route("$3", methods=["$2"])
@tag(["$1"])
@validate_response(Schema, 200)
async def handler():
    # Implementation
    pass
```

Would you like me to proceed with creating this route?
