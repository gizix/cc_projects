---
description: Show database migration status
allowed-tools: Bash(*)
model: sonnet
---

Display current database migration status including version, pending migrations, and history.

## Usage

```bash
/db-status
```

## What This Does

Shows:
- Current migration version
- Pending migrations (if any)
- Recent migration history
- Database connection status
- Schema state

## Command

```bash
echo "=== Current Database Version ==="
alembic current
echo ""
echo "=== Migration History ==="
alembic history --verbose
echo ""
echo "=== Pending Migrations ==="
alembic upgrade --sql head | head -20 || echo "Database is up to date"
```

## Output Interpretation

**Current Version:**
- Shows current revision ID
- Displays migration message
- Indicates if database is empty

**History:**
- Lists all migrations
- Shows timestamps
- Indicates applied vs pending
- Arrow (→) shows current position

**Pending:**
- SQL preview of next migration
- Shows what will be applied
- Empty if database is current

## Common Scenarios

**Database is current:**
```
Current: abc123def456 (add user table)
No pending migrations
```

**Migrations pending:**
```
Current: abc123def456 (add user table)
Pending: xyz789ghi012 (add posts table)
```

**Fresh database:**
```
Current: None
Multiple migrations pending
```

## Notes

- No database changes made (read-only)
- Safe to run anytime
- Useful before `/db-upgrade`
- Check after pulling new code
