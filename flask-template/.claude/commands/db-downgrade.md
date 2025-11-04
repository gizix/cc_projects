---
description: Rollback database migration
argument-hint: "[REVISION]"
---

Rollback database to a previous migration revision.

## Arguments

- `REVISION` (optional): Target revision to downgrade to
  - `-1`: Rollback one migration
  - `-2`: Rollback two migrations
  - `abc123`: Rollback to specific revision
  - `base`: Rollback all migrations

## Examples

```bash
# Rollback last migration
flask db downgrade -1

# Rollback to specific revision
flask db downgrade abc123def

# Rollback all migrations
flask db downgrade base
```

## Warnings

- **CAUTION**: Downgrading may result in data loss
- Always backup database before downgrading
- Review the down() function in migration file
- Test downgrade on development database first
- Some migrations may not be reversible

## When to Downgrade

- Testing migration changes
- Rolling back problematic migrations
- Reverting to previous schema version
- Development and testing scenarios

## Notes

- Production downgrades should be carefully planned
- Consider data preservation strategies
- Document downgrade procedures
- Have recovery plan in place

Execute: `cd flask-template && flask db downgrade $ARGUMENTS`
