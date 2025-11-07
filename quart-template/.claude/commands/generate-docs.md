---
description: Generate OpenAPI documentation
---

Access and export the auto-generated OpenAPI documentation.

Quart-Schema automatically generates OpenAPI 3.0 documentation from your routes and schemas.

## Access Documentation

Start the development server:
```bash
cd quart-template && QUART_APP="src.app:create_app()" quart run
```

Then visit:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redocs
- **Scalar**: http://localhost:5000/scalar
- **OpenAPI JSON**: http://localhost:5000/openapi.json

## Export OpenAPI Specification

Save the OpenAPI spec to a file:
```bash
curl http://localhost:5000/openapi.json > openapi.json
```

Or using Python:
```python
import asyncio
import json

async def export_openapi():
    from src.app import create_app
    app = await create_app("development")

    with open("openapi.json", "w") as f:
        json.dump(app.extensions["QUART_SCHEMA"].openapi, f, indent=2)

asyncio.run(export_openapi())
```

## What's Documented

The OpenAPI spec includes:
- All routes with @tag decorators
- Request/response schemas from @validate_* decorators
- Authentication requirements
- Parameter descriptions from Pydantic models
- Response codes and error schemas

Add more detail by enhancing your Pydantic schemas with Field descriptions.
