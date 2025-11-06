"""Token Pydantic schemas for authentication."""

from pydantic import BaseModel


class Token(BaseModel):
    """Access token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str  # Subject (user identifier)
    exp: int  # Expiration timestamp
