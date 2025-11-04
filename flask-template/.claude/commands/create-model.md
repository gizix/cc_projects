---
description: Generate SQLAlchemy model with fields
argument-hint: "<ModelName> [field:Type ...]"
---

Generate a new SQLAlchemy model with specified fields.

## Arguments

- `ModelName` (required): Name of the model class (PascalCase)
- `field:Type`: Field definitions (optional)

## Field Types

- `String`, `String(length)`: Variable-length string
- `Integer`: Integer field
- `Boolean`: Boolean field
- `DateTime`: Datetime field
- `Text`: Large text field
- `Float`: Floating point number
- `ForeignKey(table.id)`: Foreign key relationship

## Examples

```bash
# Create Post model with fields
/create-model Post title:String content:Text user_id:ForeignKey(users.id)

# Create Category model
/create-model Category name:String(50) description:Text

# Create Comment model
/create-model Comment content:Text post_id:ForeignKey(posts.id) user_id:ForeignKey(users.id)
```

## What Gets Created

1. Model file in `app/models/{model_name}.py`
2. Model includes:
   - Primary key `id` field
   - Specified fields with appropriate types
   - `created_at` and `updated_at` timestamps
   - `__repr__` method
   - `to_dict()` serialization method

3. Updates `app/models/__init__.py` to import new model

## Notes

- Follow SQLAlchemy column naming (snake_case)
- Add indexes and constraints as needed after generation
- Remember to create migration after adding model
- Consider adding relationships and validators

Provide arguments as: $1 (ModelName) $2 (fields...)
