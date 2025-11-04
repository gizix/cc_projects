# Flask REST API Template - Claude Code Context

This document provides comprehensive context for working with this Flask REST API template.

## Project Overview

This is a production-ready Flask 3.x template featuring:
- **REST API** with JWT authentication
- **SQLAlchemy ORM** with Flask-Migrate for database management
- **Marshmallow** for serialization and validation
- **Pytest** for comprehensive testing
- **Docker** support for containerized deployment
- **Code quality tools** (Black, flake8, mypy)

## Architecture Patterns

### Application Factory Pattern

The application uses the factory pattern for creating Flask app instances:

```python
# app/__init__.py
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    # ...

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app
```

**Why**: Enables multiple app instances (testing, production), simplifies testing, and allows configuration flexibility.

### Blueprint Organization

API endpoints are organized into modular blueprints:

```
app/api/
├── __init__.py       # Blueprint registry
├── auth.py           # Authentication endpoints
├── users.py          # User management
└── resources.py      # Resource CRUD
```

Each blueprint handles a specific domain and registers with a URL prefix.

### Service Layer Pattern

Business logic is separated from routes into service classes:

```python
# app/services/user_service.py
class UserService:
    @staticmethod
    def create_user(username, email, password):
        # Business logic here
        pass
```

**Why**: Keeps routes thin, makes business logic reusable and testable independently.

## Project Structure

```
flask-template/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration classes
│   ├── extensions.py            # Extension initialization
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── api/                     # API blueprints
│   │   ├── __init__.py
│   │   ├── auth.py             # /api/auth/*
│   │   ├── users.py            # /api/users/*
│   │   └── resources.py        # /api/resources/*
│   ├── schemas/                 # Marshmallow schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── user_service.py
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── decorators.py
│       └── validators.py
├── migrations/                   # Database migrations
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── test_models.py
│   └── test_api.py
├── instance/                     # Instance-specific files
├── .claude/                      # Claude Code configuration
│   ├── commands/                # Slash commands
│   ├── agents/                  # Specialized agents
│   ├── skills/                  # Automated skills
│   └── settings.json
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── wsgi.py                       # WSGI entry point
├── Dockerfile
├── docker-compose.yml
├── CLAUDE.md                     # This file
└── README.md                     # User documentation
```

## Flask Conventions

### Models (app/models/)

SQLAlchemy models define database schema:

```python
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Serialize to dictionary (exclude sensitive fields)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active
        }
```

**Conventions**:
- Use `__tablename__` explicitly
- Add indexes on foreign keys and frequently queried columns
- Never expose password hashes in to_dict()
- Use `created_at` and `updated_at` timestamps
- Implement `__repr__` for debugging

### Schemas (app/schemas/)

Marshmallow schemas handle serialization and validation:

```python
from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma

class UserCreateSchema(ma.Schema):
    """Schema for creating users."""
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8), load_only=True)

    @validates('email')
    def validate_email_unique(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')
```

**Conventions**:
- Separate schemas for create/read/update operations
- Use `load_only=True` for sensitive fields (passwords)
- Use `dump_only=True` for system fields (id, timestamps)
- Validate uniqueness at schema level
- Use custom validators for business rules

### API Blueprints (app/api/)

RESTful API endpoints follow conventions:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """GET /api/users - List all users."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = User.query.paginate(page=page, per_page=per_page)

    return jsonify({
        'users': users_schema.dump(pagination.items),
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    }), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """GET /api/users/:id - Get specific user."""
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user)), 200
```

**REST Conventions**:
- `GET /resources` - List (with pagination)
- `POST /resources` - Create
- `GET /resources/:id` - Read one
- `PUT /resources/:id` - Replace (full update)
- `PATCH /resources/:id` - Update (partial)
- `DELETE /resources/:id` - Delete

**HTTP Status Codes**:
- 200 OK - Successful GET, PUT, PATCH
- 201 Created - Successful POST
- 204 No Content - Successful DELETE
- 400 Bad Request - Validation error
- 401 Unauthorized - Authentication required
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource doesn't exist
- 500 Internal Server Error - Server error

### Authentication & Authorization

#### JWT Authentication

```python
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token})

    return jsonify({'error': 'Invalid credentials'}), 401

# Protected endpoint
@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.to_dict())
```

**Security Best Practices**:
- Never store passwords in plain text (use bcrypt)
- Use separate secret keys for JWT and session
- Set appropriate token expiration times
- Implement token refresh mechanism
- Consider token blacklisting for logout

### Database Migrations

Use Flask-Migrate (Alembic) for schema changes:

```bash
# Create migration after model changes
flask db migrate -m "add user profile fields"

# Review generated migration in migrations/versions/

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade -1
```

**Migration Best Practices**:
- Always review auto-generated migrations
- One logical change per migration
- Test migrations on development first
- Handle data transformations carefully
- Provide downgrade implementations

### Testing with Pytest

Comprehensive testing using pytest:

```python
# tests/test_api.py
def test_user_registration(client):
    """Test user can register."""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'SecurePass123!'
    })

    assert response.status_code == 201
    assert 'user' in response.json

def test_login_with_valid_credentials(client, sample_user):
    """Test login with valid credentials."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPassword123!'
    })

    assert response.status_code == 200
    assert 'access_token' in response.json
```

**Testing Conventions**:
- Use fixtures for test data (conftest.py)
- Test happy path and error cases
- Test authentication/authorization
- Use descriptive test names
- Aim for high coverage (>90%)

## Configuration Management

### Environment-Based Configuration

```python
# app/config.py
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

    # Validate required environment variables
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY must be set in production")
```

**Configuration Hierarchy**:
1. Default values in Config class
2. Environment-specific overrides
3. Environment variables (.env file)
4. Instance configuration (instance/)

## Security Considerations

### Input Validation

Always validate user input with Marshmallow schemas:

```python
try:
    data = user_create_schema.load(request.json)
except ValidationError as err:
    return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
```

### SQL Injection Prevention

SQLAlchemy ORM automatically uses parameterized queries:

```python
# SAFE - SQLAlchemy parameterizes automatically
user = User.query.filter_by(email=email).first()

# SAFE - Using text() with parameters
from sqlalchemy import text
result = db.session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": email}
)

# NEVER DO THIS - vulnerable to SQL injection
# query = f"SELECT * FROM users WHERE email = '{email}'"  # DANGEROUS!
```

### Password Security

Use Flask-Bcrypt or werkzeug.security for password hashing:

```python
from app.extensions import bcrypt

class User(db.Model):
    password_hash = db.Column(db.String(255), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
```

### CORS Configuration

Configure CORS restrictively in production:

```python
from flask_cors import CORS

# Development - allow all origins
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Production - restrict origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Security Headers

Add security headers to responses:

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if app.config.get('SESSION_COOKIE_SECURE'):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## Common Operations

### Adding a New Model

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Create migration: `flask db migrate -m "add model_name"`
4. Apply migration: `flask db upgrade`
5. Create schema in `app/schemas/`
6. Add API blueprint if needed

### Adding a New API Endpoint

1. Create/update blueprint in `app/api/`
2. Define route with appropriate HTTP method
3. Add `@jwt_required()` if authentication needed
4. Use schema for validation
5. Return JSON response with status code
6. Write tests in `tests/test_api.py`

### Adding Custom Validation

In Marshmallow schema:

```python
from marshmallow import validates, ValidationError

class UserSchema(ma.Schema):
    username = fields.String()

    @validates('username')
    def validate_username(self, value):
        if len(value) < 3:
            raise ValidationError('Username must be at least 3 characters')
        if not value.isalnum():
            raise ValidationError('Username must be alphanumeric')
```

## Development Workflow

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Seed database (optional)
flask seed-db

# Run development server
flask run

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Docker Development

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations in container
docker-compose exec web flask db upgrade

# Run tests in container
docker-compose exec web pytest

# Stop services
docker-compose down
```

## Performance Optimization

### N+1 Query Prevention

Use eager loading with joinedload/selectinload:

```python
from sqlalchemy.orm import joinedload, selectinload

# N+1 problem - BAD
users = User.query.all()
for user in users:
    print(user.posts)  # Separate query for each user!

# Solution with eager loading - GOOD
users = User.query.options(selectinload(User.posts)).all()
for user in users:
    print(user.posts)  # Loaded in advance
```

### Pagination

Always paginate list endpoints:

```python
@users_bp.route('', methods=['GET'])
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    pagination = User.query.paginate(page=page, per_page=per_page)

    return jsonify({
        'users': users_schema.dump(pagination.items),
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })
```

### Database Indexing

Add indexes on frequently queried columns:

```python
class User(db.Model):
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), index=True)
```

## Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure `DATABASE_URL` for PostgreSQL
- [ ] Set restrictive CORS origins
- [ ] Enable secure session cookies
- [ ] Use HTTPS with SSL certificates
- [ ] Configure gunicorn with appropriate workers
- [ ] Set up logging (not to stdout)
- [ ] Enable rate limiting
- [ ] Set up monitoring and error tracking
- [ ] Configure database connection pooling
- [ ] Review security headers
- [ ] Test migrations on staging
- [ ] Backup database before deployment

### Production Server (Gunicorn)

```bash
# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 wsgi:app

# With environment variables
FLASK_ENV=production DATABASE_URL=postgresql://... gunicorn wsgi:app
```

## Troubleshooting

### Common Issues

**ImportError**: Module not found
- Verify virtual environment is activated
- Run `pip install -r requirements.txt`

**Database errors**: Table doesn't exist
- Run migrations: `flask db upgrade`
- Check database URL in .env

**Authentication errors**: Invalid token
- Check JWT_SECRET_KEY matches between requests
- Verify token hasn't expired
- Check Authorization header format

**CORS errors**: Blocked by CORS policy
- Check CORS_ORIGINS configuration
- Verify origin is allowed
- Check request methods and headers

## Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Marshmallow Documentation**: https://marshmallow.readthedocs.io/
- **Flask-JWT-Extended**: https://flask-jwt-extended.readthedocs.io/
- **pytest Documentation**: https://docs.pytest.org/

---

This template provides a solid foundation for building production-ready Flask REST APIs. Customize and extend based on your specific requirements.
