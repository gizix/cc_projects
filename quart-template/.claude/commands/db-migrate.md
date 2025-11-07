---
description: Generate/apply database migrations
argument-hint: "[message]"
---

Manage database migrations using Alembic.

Arguments:
- $1: Optional migration message (e.g., "add user table")

**Note**: This template uses auto table creation in development mode. For production, you should set up Alembic migrations.

## Setup Alembic (First Time)

```bash
cd quart-template
pip install alembic
alembic init alembic
```

Then configure alembic/env.py to use async SQLAlchemy.

## Common Migration Commands

Create new migration:
```bash
alembic revision --autogenerate -m "$ARGUMENTS"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback one migration:
```bash
alembic downgrade -1
```

View migration history:
```bash
alembic history
```

Current migration status:
```bash
alembic current
```

## Development Mode

In development, tables are auto-created on app startup. Migrations are optional but recommended for tracking schema changes.

## Production

Always use migrations in production:
1. Generate migration: `alembic revision --autogenerate`
2. Review generated migration file
3. Test migration: `alembic upgrade head`
4. Commit migration file to version control
