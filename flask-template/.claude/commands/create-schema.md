---
description: Generate Marshmallow schema for model
argument-hint: "<ModelName>"
---

Generate Marshmallow serialization schemas for a model.

## Arguments

- `ModelName` (required): Name of the model to create schema for

## What Gets Created

Creates three schemas in `app/schemas/{model_name}.py`:

1. **{Model}Schema**: For serialization (read operations)
   - Includes all model fields
   - Excludes sensitive data
   - Dump-only fields (id, timestamps)

2. **{Model}CreateSchema**: For creating new instances
   - Required fields validation
   - Custom validators
   - Load-only sensitive fields

3. **{Model}UpdateSchema**: For updating instances
   - All fields optional
   - Partial updates supported
   - Validation rules

## Examples

```bash
# Create schema for Post model
/create-schema Post

# Create schema for Comment model
/create-schema Comment
```

## Generated Features

- Field type mapping from SQLAlchemy to Marshmallow
- Automatic validation
- Custom error messages
- Nested schemas for relationships
- Pre/post load/dump hooks
- Required vs optional fields

## Notes

- Schema file created in `app/schemas/`
- Imported in `app/schemas/__init__.py`
- Follows Marshmallow best practices
- Separates read/write schemas for security
- Ready to use in API endpoints

Provide the model name as $1 argument.
