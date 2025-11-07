"""Pydantic schemas for request/response validation.

These schemas are used with Quart-Schema for automatic validation
and OpenAPI documentation generation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Authentication Schemas
class UserRegisterSchema(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=80, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLoginSchema(BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class TokenSchema(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class UserSchema(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# Item Schemas
class ItemCreateSchema(BaseModel):
    """Schema for creating a new item."""

    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(
        None, max_length=500, description="Item description"
    )
    price: float = Field(..., gt=0, description="Item price (must be positive)")
    is_available: bool = Field(default=True, description="Item availability status")


class ItemUpdateSchema(BaseModel):
    """Schema for updating an existing item."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None


class ItemSchema(BaseModel):
    """Schema for item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    price: float = Field(..., description="Item price")
    is_available: bool = Field(..., description="Availability status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# Pagination Schemas
class PaginatedItemsSchema(BaseModel):
    """Schema for paginated items response."""

    items: list[ItemSchema] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


# Error Schemas
class ErrorSchema(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


# WebSocket Schemas
class WebSocketMessageSchema(BaseModel):
    """Schema for WebSocket messages."""

    type: str = Field(..., description="Message type")
    payload: dict = Field(..., description="Message payload")
    timestamp: Optional[datetime] = Field(
        None, description="Message timestamp"
    )
