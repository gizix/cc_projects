---
description: Open Flask interactive shell with app context
argument-hint: "[--ipython]"
---

Open an interactive Python shell with the Flask application context loaded.

## Arguments

- `--ipython`: Use IPython if available (enhanced shell with autocompletion)

## Usage

The Flask shell automatically imports the `app` object and provides access to:
- Database models
- Extensions (db, jwt, etc.)
- Application configuration
- All imports from your application

## Examples

```bash
# Start standard Flask shell
flask shell

# Start with IPython (if installed)
flask shell --ipython
```

## Common Commands

```python
# Access the database
from app.models.user import User
users = User.query.all()

# Create a new user
user = User(username='test', email='test@example.com', password='password')
db.session.add(user)
db.session.commit()

# Access configuration
app.config['SECRET_KEY']

# Test functions
from app.services.auth_service import AuthService
AuthService.authenticate_user('test@example.com', 'password')
```

Execute: `cd flask-template && flask shell $ARGUMENTS`
