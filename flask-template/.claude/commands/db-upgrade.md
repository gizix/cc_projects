---
description: Run database migrations
argument-hint: "[REVISION]"
---

Apply database migrations using Flask-Migrate.

## Arguments

- `REVISION` (optional): Specific revision to upgrade to (default: 'head' - latest)

## Examples

```bash
# Upgrade to latest migration
flask db upgrade

# Upgrade to specific revision
flask db upgrade abc123

# Upgrade one step forward
flask db upgrade +1
```

## Notes

- Ensure database is accessible before running migrations
- Check migration status with `/db-status` command
- Review migration file before applying to understand changes
- Always backup production databases before migrating

## Related Commands

- `/db-migrate` - Create new migration
- `/db-downgrade` - Rollback migration
- `/db-status` - View migration status

Execute: `cd flask-template && flask db upgrade $ARGUMENTS`
