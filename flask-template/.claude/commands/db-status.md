---
description: Display migration status
argument-hint: ""
---

Show the current database migration status.

## Usage

```bash
flask db current
flask db history
flask db show <revision>
```

## Commands

### Current Status
```bash
# Show current revision
flask db current
```

### Migration History
```bash
# Show all migrations
flask db history

# Show recent migrations
flask db history -r-5:

# Show with details
flask db history --verbose
```

### Show Specific Migration
```bash
# Show migration details
flask db show abc123
```

## Output Information

- Current database revision
- Pending migrations
- Applied migrations
- Migration messages
- Revision hashes

## Example Output

```
Current revision: abc123def456
Message: add user role field
Parent: 789ghi012jkl
Path: migrations/versions/abc123def456_add_user_role_field.py

(head)      -> abc123def456, add user role field
abc123def456 -> 789ghi012jkl, create users table
789ghi012jkl -> (base), initial migration
```

## Notes

- Helps track migration state
- Identifies pending migrations
- Useful before deploying
- Confirms database schema version

Execute: `cd flask-template && flask db current && flask db history`
