"""User service for user management operations."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    """Service for user management operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
        self.user_repo = UserRepository(db)

    async def create_user(self, user_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_in: User creation schema with email, username, and password

        Returns:
            Created user instance

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        if await self.user_repo.email_exists(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        if await self.user_repo.username_exists(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Create user with hashed password
        user_data = {
            "email": user_in.email,
            "username": user_in.username,
            "hashed_password": get_password_hash(user_in.password),
            "is_active": user_in.is_active,
        }

        user = await self.user_repo.create(user_data)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User's ID

        Returns:
            User instance or None if not found
        """
        return await self.user_repo.get(user_id)
