---
description: Add SQLAlchemy model with migrations
argument-hint: "<model-name> [fields...]"
---

Create a new SQLAlchemy async model in the project.

Arguments:
- $1: Model name (e.g., "Product", "Order")
- $2+: Optional field definitions (will prompt if not provided)

I'll help you create a new SQLAlchemy model for "$1".

Steps I'll take:
1. Create model class in `src/app/models/__init__.py`
2. Add proper type hints using SQLAlchemy 2.0 Mapped types
3. Include timestamps (created_at, updated_at)
4. Add `to_dict()` serialization method
5. Create corresponding Pydantic schemas in `src/app/schemas/__init__.py`

Would you like me to:
a) Create a basic model with common fields (id, created_at, updated_at)
b) Specify custom fields now
c) Let me suggest fields based on the model name

After creating the model, you'll need to:
- Restart the app to create the table (development mode auto-creates tables)
- Or use migrations (Alembic) for production
