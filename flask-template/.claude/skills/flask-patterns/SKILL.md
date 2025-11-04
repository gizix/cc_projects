---
description: Implement common Flask design patterns including application factory, blueprints, service layer, decorators, and context managers
allowed-tools: [Read, Write, Grep]
---

This skill provides implementation patterns for common Flask architectural patterns and best practices.

## When This Skill Activates

This skill automatically activates when:
- Refactoring Flask application structure
- Implementing architectural patterns
- Organizing code for better maintainability
- Setting up new Flask features following best practices

## Patterns Provided

### 1. Application Factory Pattern

**Purpose**: Create multiple app instances with different configurations

```python
# app/__init__.py
from flask import Flask
from app.config import config
from app.extensions import db, migrate, jwt, cors, ma, bcrypt

def create_app(config_name='development'):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.api import auth_bp, users_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    # Register error handlers
    register_error_handlers(app)

    # Register CLI commands
    register_cli_commands(app)

    return app
```

### 2. Extension Initialization Pattern

**Purpose**: Centralize extension initialization

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt

# Create instances without app
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()
bcrypt = Bcrypt()

# Initialize in factory with init_app()
```

### 3. Service Layer Pattern

**Purpose**: Separate business logic from routes

```python
# app/services/user_service.py
from app.models.user import User
from app.extensions import db

class UserService:
    """Business logic for user operations."""

    @staticmethod
    def create_user(username, email, password):
        """Create a new user."""
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already registered')

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        return User.query.get(user_id)

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user fields."""
        user = User.query.get(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.session.commit()
        return user

# Usage in routes
@users_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user = UserService.create_user(**data)
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### 4. Custom Decorator Patterns

**Authentication Decorator**:
```python
# app/utils/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def admin_required():
    """Require admin role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.route('/admin/users')
@jwt_required()
@admin_required()
def admin_users():
    pass
```

**Permission Decorator**:
```python
def permission_required(permission):
    """Check specific permission."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user.has_permission(permission):
                return jsonify({'error': f'Permission denied: {permission}'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

**Resource Owner Decorator**:
```python
def owner_required(get_resource_fn):
    """Ensure user owns resource."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            resource = get_resource_fn(**kwargs)

            if resource.user_id != user_id:
                return jsonify({'error': 'Access denied'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

### 5. Context Manager Pattern

**Database Session Management**:
```python
from contextlib import contextmanager

@contextmanager
def db_session():
    """Provide a transactional scope."""
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
        db.session.close()

# Usage
with db_session() as session:
    user = User(username='test')
    session.add(user)
```

### 6. Request/Response Hook Patterns

**Before Request**:
```python
@app.before_request
def before_request():
    """Run before each request."""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())

@app.after_request
def after_request(response):
    """Run after each request."""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        response.headers['X-Response-Time'] = f'{elapsed:.3f}s'
        response.headers['X-Request-ID'] = g.request_id

    return response
```

### 7. Error Handler Pattern

```python
def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
```

### 8. CLI Command Pattern

```python
def register_cli_commands(app):
    """Register custom CLI commands."""

    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Database initialized.')

    @app.cli.command('seed-db')
    @click.option('--users', default=10, help='Number of users to create')
    def seed_db(users):
        """Seed database with sample data."""
        for i in range(users):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password123'
            )
            db.session.add(user)

        db.session.commit()
        click.echo(f'Created {users} users.')
```

### 9. Configuration Pattern

```python
# app/config.py
import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY must be set in production")

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 10. Model Mixin Pattern

```python
# app/models/mixins.py
from datetime import datetime
from app.extensions import db

class TimestampMixin:
    """Add created_at and updated_at timestamps."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SoftDeleteMixin:
    """Add soft delete functionality."""
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)

    def soft_delete(self):
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
        db.session.commit()

# Usage
class User(db.Model, TimestampMixin, SoftDeleteMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
```

## When to Use Each Pattern

- **Application Factory**: Always use in production Flask apps
- **Service Layer**: For complex business logic
- **Decorators**: For reusable authentication/authorization
- **Context Managers**: For resource management (db, files, locks)
- **Hooks**: For request-level logic (logging, timing, headers)
- **Error Handlers**: For consistent error responses
- **CLI Commands**: For administrative tasks
- **Mixins**: For common model behavior

This skill helps you implement Flask best practices automatically.
