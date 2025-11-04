---
description: Create new migration from model changes
argument-hint: "[-m MESSAGE]"
---

Generate a new database migration based on detected model changes.

## Arguments

- `-m MESSAGE`: Migration message describing the changes (required)

## Examples

```bash
# Create migration with descriptive message
flask db migrate -m "add user role field"

# Create migration for new table
flask db migrate -m "create posts table"

# Create migration for relationship changes
flask db migrate -m "add user to posts relationship"
```

## Workflow

1. Make changes to your models (e.g., add fields, create new models)
2. Run `flask db migrate -m "description"` to generate migration
3. Review the generated migration file in `migrations/versions/`
4. Run `flask db upgrade` to apply the migration

## Notes

- Always review generated migrations before applying
- Migration message should be descriptive and use present tense
- Alembic may not detect all changes (e.g., column type changes)
- Manual adjustments to migration files may be necessary
- Test migrations on development database first

## Migration Best Practices

- One logical change per migration
- Use descriptive messages
- Add data migrations when needed
- Test rollback with downgrade

Execute: `cd flask-template && flask db migrate $ARGUMENTS`
