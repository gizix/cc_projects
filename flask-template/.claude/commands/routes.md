---
description: Display all registered routes
argument-hint: "[--sort] [--blueprint NAME]"
---

Display all registered Flask routes and endpoints.

## Arguments

- `--sort`: Sort routes alphabetically
- `--blueprint NAME`: Filter by blueprint name

## Examples

```bash
# Show all routes
flask routes

# Show routes sorted
flask routes --sort

# Show only auth routes
flask routes | grep auth

# Show with methods
flask routes
```

## Output Format

The command displays:
- Endpoint name
- HTTP methods
- URL pattern
- View function

## Example Output

```
Endpoint              Methods    Rule
--------------------  ---------  ------------------------
auth.login            POST       /api/auth/login
auth.register         POST       /api/auth/register
auth.me               GET        /api/auth/me
auth.refresh          POST       /api/auth/refresh
users.get_users       GET        /api/users
users.get_user        GET        /api/users/<int:user_id>
```

## Notes

- Useful for debugging routing issues
- Shows all blueprints and their prefixes
- Helps verify route registration
- Identifies duplicate or conflicting routes

Execute: `cd flask-template && flask routes $ARGUMENTS`
