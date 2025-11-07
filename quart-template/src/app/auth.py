"""JWT authentication utilities and middleware.

This module provides JWT token generation, validation, and authentication
decorators for protecting routes.
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable, Any

from quart import request, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Hash a password using werkzeug's secure hash.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against its hash.

    Args:
        password_hash: Hashed password
        password: Plain text password to verify

    Returns:
        True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)


def create_access_token(user_id: int, username: str) -> str:
    """Create a JWT access token.

    Args:
        user_id: User ID
        username: Username

    Returns:
        JWT access token string
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "type": "access",
        "exp": datetime.utcnow() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def create_refresh_token(user_id: int, username: str) -> str:
    """Create a JWT refresh token.

    Args:
        user_id: User ID
        username: Username

    Returns:
        JWT refresh token string
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "type": "refresh",
        "exp": datetime.utcnow() + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
        return payload
    except jwt.ExpiredSignatureError:
        current_app.logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        current_app.logger.warning(f"Invalid token: {e}")
        return None


async def get_current_user() -> Optional[dict]:
    """Extract and validate current user from JWT token.

    Returns:
        User info dict if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        return None

    return {
        "user_id": payload["user_id"],
        "username": payload["username"],
    }


def require_auth(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require JWT authentication for a route.

    Usage:
        @app.route('/protected')
        @require_auth
        async def protected_route():
            user = g.current_user
            return {'message': f'Hello {user["username"]}'}

    Args:
        f: Route handler function

    Returns:
        Wrapped function that requires authentication
    """

    @wraps(f)
    async def decorated_function(*args: Any, **kwargs: Any) -> Any:
        user = await get_current_user()

        if user is None:
            return {"error": "Unauthorized", "message": "Valid token required"}, 401

        # Store user info in request context
        g.current_user = user

        return await f(*args, **kwargs)

    return decorated_function


def optional_auth(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to optionally load authenticated user.

    If a valid token is provided, user info is available in g.current_user.
    Otherwise, g.current_user is None and route execution continues.

    Args:
        f: Route handler function

    Returns:
        Wrapped function with optional authentication
    """

    @wraps(f)
    async def decorated_function(*args: Any, **kwargs: Any) -> Any:
        user = await get_current_user()
        g.current_user = user
        return await f(*args, **kwargs)

    return decorated_function
