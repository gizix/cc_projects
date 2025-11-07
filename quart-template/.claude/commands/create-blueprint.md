---
description: Generate new blueprint structure
argument-hint: "<blueprint-name> [url-prefix]"
---

Create a new Quart blueprint with the standard structure.

Arguments:
- $1: Blueprint name (e.g., "users", "products")
- $2: Optional URL prefix (default: /api/$1)

I'll create the following for your blueprint "$1":

1. Create blueprint directory: `src/app/routes/$1/`
2. Create `__init__.py` with blueprint registration
3. Add example route with validation
4. Register blueprint in `src/app/__init__.py`

Would you like me to proceed with creating the "$1" blueprint?

After confirmation, I'll:
- Create the blueprint file with proper imports
- Add example GET and POST routes
- Include Quart-Schema validation decorators
- Register it in the application factory
- Add error handlers if needed
