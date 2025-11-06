"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.token import Token
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    OAuth2 compatible token login.

    Get an access token for future requests by providing username and password.

    Args:
        form_data: OAuth2 form with username and password
        db: Database session

    Returns:
        Token with access_token and token_type
    """
    auth_service = AuthService(db)
    return await auth_service.authenticate(form_data.username, form_data.password)
