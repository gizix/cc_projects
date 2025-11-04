---
description: Implement authentication and authorization systems including JWT, session-based, role-based access control (RBAC), and OAuth integration
allowed-tools: [Read, Write, Grep]
---

This skill provides complete authentication and authorization system implementations for Flask applications.

## When This Skill Activates

Automatically activates when:
- Implementing authentication systems
- Adding JWT token handling
- Creating login/registration flows
- Implementing role-based access control
- Protecting API endpoints

## JWT Authentication System

### Complete Auth Implementation

```python
# app/api/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError
from app.extensions import db
from app.models.user import User
from app.schemas.user import UserCreateSchema, LoginSchema, UserSchema

auth_bp = Blueprint('auth', __name__)

# Initialize schemas
user_create_schema = UserCreateSchema()
login_schema = LoginSchema()
user_schema = UserSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = user_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens."""
    try:
        data = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401

    # Create tokens with additional claims
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role}
    )
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': user_schema.dump(user)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_active:
        return jsonify({'error': 'Invalid user'}), 401

    access_token = create_access_token(
        identity=current_user_id,
        additional_claims={'role': user.role}
    )

    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user_schema.dump(user)), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token should be blacklisted)."""
    jti = get_jwt()['jti']
    # TODO: Add jti to token blacklist (Redis recommended)
    return jsonify({'message': 'Successfully logged out'}), 200
```

## Role-Based Access Control (RBAC)

### User Model with Roles

```python
# app/models/user.py
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # user, moderator, admin
    is_active = db.Column(db.Boolean, default=True)

    def has_role(self, role):
        """Check if user has specific role."""
        roles_hierarchy = {
            'user': 1,
            'moderator': 2,
            'admin': 3
        }
        return roles_hierarchy.get(self.role, 0) >= roles_hierarchy.get(role, 0)
```

### Role-Based Decorators

```python
# app/utils/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.models.user import User

def role_required(required_role):
    """Require specific role or higher."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.has_role(required_role):
                return jsonify({'error': f'{required_role.title()} access required'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required():
    """Require admin role."""
    return role_required('admin')

def moderator_required():
    """Require moderator role or higher."""
    return role_required('moderator')


# Usage
@app.route('/admin/users')
@jwt_required()
@admin_required()
def admin_users():
    """Admin-only endpoint."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/moderate/posts')
@jwt_required()
@moderator_required()
def moderate_posts():
    """Moderator-only endpoint."""
    posts = Post.query.filter_by(flagged=True).all()
    return jsonify([post.to_dict() for post in posts])
```

## Permission-Based Access Control

### Permission Model

```python
# app/models/permission.py
from app.extensions import db

# Association table
user_permissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

class User(db.Model):
    # ... existing fields ...
    permissions = db.relationship('Permission', secondary=user_permissions, backref='users')

    def has_permission(self, permission_name):
        """Check if user has specific permission."""
        return any(p.name == permission_name for p in self.permissions)

    def add_permission(self, permission_name):
        """Add permission to user."""
        permission = Permission.query.filter_by(name=permission_name).first()
        if permission and permission not in self.permissions:
            self.permissions.append(permission)
```

### Permission Decorator

```python
def permission_required(*required_permissions):
    """Require specific permissions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            for permission in required_permissions:
                if not user.has_permission(permission):
                    return jsonify({'error': f'Permission denied: {permission}'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Usage
@app.route('/posts/<int:id>/edit')
@jwt_required()
@permission_required('edit_posts')
def edit_post(id):
    """Edit post - requires 'edit_posts' permission."""
    pass
```

## Token Blacklisting (Redis)

```python
# app/extensions.py
from flask_jwt_extended import JWTManager
import redis

jwt = JWTManager()
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# app/__init__.py
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token is revoked."""
    jti = jwt_payload['jti']
    token_in_redis = redis_client.get(jti)
    return token_in_redis is not None

# Logout endpoint
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout and blacklist token."""
    jti = get_jwt()['jti']
    # Store token with expiration matching JWT expiration
    redis_client.setex(jti, 3600, 'true')  # 1 hour
    return jsonify({'message': 'Successfully logged out'}), 200
```

## Password Reset Flow

```python
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset."""
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()

    if user:
        # Generate reset token
        reset_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1),
            additional_claims={'type': 'password_reset'}
        )

        # Send email with reset link
        # send_password_reset_email(user.email, reset_token)

    # Always return success (security: don't reveal if email exists)
    return jsonify({'message': 'If email exists, reset link has been sent'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
@jwt_required()
def reset_password():
    """Reset password with token."""
    claims = get_jwt()

    # Verify token type
    if claims.get('type') != 'password_reset':
        return jsonify({'error': 'Invalid token type'}), 400

    user_id = get_jwt_identity()
    new_password = request.json.get('password')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.password = new_password
    db.session.commit()

    return jsonify({'message': 'Password reset successfully'}), 200
```

## OAuth 2.0 Integration (Google Example)

```python
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route('/login/google')
def google_login():
    """Redirect to Google OAuth."""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/google')
def google_callback():
    """Handle Google OAuth callback."""
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)

    # Find or create user
    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        user = User(
            username=user_info['email'].split('@')[0],
            email=user_info['email'],
            password=secrets.token_urlsafe(32)  # Random password
        )
        db.session.add(user)
        db.session.commit()

    # Create JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })
```

This skill provides production-ready authentication and authorization systems.
