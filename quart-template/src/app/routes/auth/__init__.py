"""Authentication blueprint.

This blueprint handles user registration, login, token refresh, and user info.
"""

from quart import Blueprint
from quart_schema import validate_request, validate_response, tag
from sqlalchemy import select

from ...models import get_session, User
from ...schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    TokenSchema,
    UserSchema,
    ErrorSchema,
)
from ...auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    require_auth,
    decode_token,
)
from quart import g, request

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@tag(["auth"])
@validate_request(UserRegisterSchema)
@validate_response(UserSchema, 201)
@validate_response(ErrorSchema, 400)
async def register(data: UserRegisterSchema):
    """Register a new user.

    Creates a new user account with the provided credentials.
    """
    async with get_session() as session:
        # Check if username already exists
        result = await session.execute(
            select(User).where(User.username == data.username)
        )
        if result.scalar_one_or_none():
            return {"error": "Bad Request", "message": "Username already exists"}, 400

        # Check if email already exists
        result = await session.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            return {"error": "Bad Request", "message": "Email already exists"}, 400

        # Create new user
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user.to_dict(), 201


@auth_bp.route("/login", methods=["POST"])
@tag(["auth"])
@validate_request(UserLoginSchema)
@validate_response(TokenSchema, 200)
@validate_response(ErrorSchema, 401)
async def login(data: UserLoginSchema):
    """Login and receive JWT tokens.

    Authenticates user and returns access and refresh tokens.
    """
    async with get_session() as session:
        # Find user by username
        result = await session.execute(
            select(User).where(User.username == data.username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(user.password_hash, data.password):
            return {"error": "Unauthorized", "message": "Invalid credentials"}, 401

        # Generate tokens
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }, 200


@auth_bp.route("/refresh", methods=["POST"])
@tag(["auth"])
@validate_response(TokenSchema, 200)
@validate_response(ErrorSchema, 401)
async def refresh():
    """Refresh access token using refresh token.

    Exchanges a valid refresh token for a new access token.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Unauthorized", "message": "Token required"}, 401

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        return {"error": "Unauthorized", "message": "Invalid refresh token"}, 401

    # Generate new access token
    access_token = create_access_token(payload["user_id"], payload["username"])

    return {
        "access_token": access_token,
        "refresh_token": token,  # Return the same refresh token
        "token_type": "bearer",
    }, 200


@auth_bp.route("/me", methods=["GET"])
@tag(["auth"])
@require_auth
@validate_response(UserSchema, 200)
@validate_response(ErrorSchema, 401)
async def get_current_user_info():
    """Get current authenticated user information.

    Requires valid JWT access token in Authorization header.
    """
    user_info = g.current_user

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_info["user_id"])
        )
        user = result.scalar_one_or_none()

        if not user:
            return {"error": "Not Found", "message": "User not found"}, 404

        return user.to_dict(), 200
