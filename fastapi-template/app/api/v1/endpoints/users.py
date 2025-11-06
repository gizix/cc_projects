"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current authenticated user.

    Returns the profile of the currently logged-in user.

    Args:
        current_user: Authenticated user from token

    Returns:
        User profile data
    """
    return current_user


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Create new user.

    Register a new user with email, username, and password.

    Args:
        user_in: User creation data
        db: Database session

    Returns:
        Created user profile

    Raises:
        HTTPException: If email or username already exists
    """
    user_service = UserService(db)
    return await user_service.create_user(user_in)
