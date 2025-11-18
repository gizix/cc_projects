---
description: Create new Alembic migration
argument-hint: <message>
allowed-tools: Bash(*)
model: sonnet
---

Generate a new database migration using Alembic's async support and auto-detection.

## Arguments

- `$1`: Migration message describing the change (required)

## Usage

```bash
/db-migrate "add user table"
/db-migrate "add email index to users"
/db-migrate "create posts relationship"
```

## What This Does

1. Compares current database schema with models
2. Auto-detects changes (new tables, columns, indexes)
3. Generates migration file with upgrade/downgrade functions
4. Displays preview of changes
5. Saves migration in `alembic/versions/`

## Command

```bash
if [ -z "$1" ]; then
    echo "Error: Migration message required"
    echo "Usage: /db-migrate \"your message here\""
    exit 1
fi

echo "Generating migration: $1"
alembic revision --autogenerate -m "$1"
echo ""
echo "Migration created! Review the file in alembic/versions/"
echo "Apply with: /db-upgrade"
```

## Migration Review

Always review generated migrations:
- Check for unintended changes
- Verify data migration logic
- Ensure reversibility
- Test on development database first

## Common Patterns

```python
# Add column
op.add_column('users', sa.Column('bio', sa.String(500)))

# Add index
op.create_index('ix_users_email', 'users', ['email'])

# Add foreign key
op.add_column('posts', sa.Column('user_id', sa.Integer()))
op.create_foreign_key('fk_posts_user', 'posts', 'users', ['user_id'], ['id'])
```

## Notes

- Requires models defined in `src/app/models/`
- Migration file is timestamped
- Async operations supported
- Can be edited before applying
