---
description: Apply database migrations
allowed-tools: Bash(*)
model: sonnet
---

Apply pending database migrations to bring the database schema up to date.

## Usage

```bash
/db-upgrade
```

## What This Does

1. Checks current database version
2. Identifies pending migrations
3. Applies migrations in order
4. Updates schema version
5. Commits changes to database

## Command

```bash
echo "Applying database migrations..."
alembic upgrade head
echo "Database is now up to date!"
```

## Migration Process

Alembic will:
- Execute all pending upgrade() functions
- Track applied migrations in `alembic_version` table
- Run migrations in chronological order
- Handle async database operations
- Roll back on errors

## Safety

Before running in production:
- Backup database
- Test migrations on staging
- Review migration SQL
- Plan for downtime if needed
- Have rollback plan ready

## Troubleshooting

If migration fails:
- Check database connection
- Review migration file for errors
- Check for data conflicts
- Ensure async driver installed (asyncpg)
- Review Alembic logs

## Notes

- Always backup before migrating production
- Migrations are transactional (when supported)
- Can upgrade to specific revision: `alembic upgrade <revision>`
- Use `/db-status` to check current state
