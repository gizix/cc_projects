---
name: api-generator
description: Generate complete CRUD API endpoints with async patterns, Pydantic validation, JWT authentication, and proper error handling. Activates when creating new API resources or routes.
allowed-tools: Read, Write
---

You provide templates and generate complete API endpoints following REST conventions and Quart async patterns.

## When to Activate

- User requests new API endpoint
- Creating CRUD operations
- "generate API for..." requests
- New resource/model creation

## CRUD Endpoint Template

```python
# src/app/routes/{resource}.py
from quart import Blueprint, request, jsonify
from quart_schema import validate_request, validate_response
from quart_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select
from app.database import get_session
from app.models.{resource} import {Resource}
from app.schemas.{resource} import (
    {Resource}CreateRequest,
    {Resource}UpdateRequest,
    {Resource}Response,
    {Resource}ListResponse
)

{resource}_bp = Blueprint('{resource}', __name__, url_prefix='/api/{resource}s')

# List all
@{resource}_bp.route('', methods=['GET'])
@jwt_required
@validate_response({Resource}ListResponse)
async def list_{resource}s():
    """List all {resource}s with pagination."""
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 20)), 100)

    async with get_session() as session:
        # Get total count
        count_query = select(func.count()).select_from({Resource})
        total = (await session.execute(count_query)).scalar()

        # Get paginated results
        offset = (page - 1) * page_size
        query = select({Resource}).limit(page_size).offset(offset)
        result = await session.execute(query)
        items = result.scalars().all()

    return {Resource}ListResponse(
        items=[item.to_dict() for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

# Get by ID
@{resource}_bp.route('/<int:{resource}_id>', methods=['GET'])
@jwt_required
@validate_response({Resource}Response)
async def get_{resource}({resource}_id: int):
    """Get {resource} by ID."""
    async with get_session() as session:
        item = await session.get({Resource}, {resource}_id)
        if not item:
            return {'error': 'Not found'}, 404

    return item.to_dict()

# Create
@{resource}_bp.route('', methods=['POST'])
@jwt_required
@validate_request({Resource}CreateRequest)
@validate_response({Resource}Response, 201)
async def create_{resource}(data: {Resource}CreateRequest):
    """Create new {resource}."""
    user_id = get_jwt_identity()

    async with get_session() as session:
        item = {Resource}(**data.dict(), user_id=user_id)
        session.add(item)
        await session.commit()
        await session.refresh(item)

    return item.to_dict(), 201

# Update
@{resource}_bp.route('/<int:{resource}_id>', methods=['PATCH'])
@jwt_required
@validate_request({Resource}UpdateRequest)
@validate_response({Resource}Response)
async def update_{resource}({resource}_id: int, data: {Resource}UpdateRequest):
    """Update {resource}."""
    user_id = get_jwt_identity()

    async with get_session() as session:
        item = await session.get({Resource}, {resource}_id)
        if not item:
            return {'error': 'Not found'}, 404

        # Check ownership
        if item.user_id != user_id:
            return {'error': 'Forbidden'}, 403

        # Update fields
        for field, value in data.dict(exclude_unset=True).items():
            setattr(item, field, value)

        await session.commit()
        await session.refresh(item)

    return item.to_dict()

# Delete
@{resource}_bp.route('/<int:{resource}_id>', methods=['DELETE'])
@jwt_required
async def delete_{resource}({resource}_id: int):
    """Delete {resource}."""
    user_id = get_jwt_identity()

    async with get_session() as session:
        item = await session.get({Resource}, {resource}_id)
        if not item:
            return {'error': 'Not found'}, 404

        # Check ownership
        if item.user_id != user_id:
            return {'error': 'Forbidden'}, 403

        await session.delete(item)
        await session.commit()

    return '', 204
```

## Schema Template

```python
# src/app/schemas/{resource}.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class {Resource}CreateRequest:
    """Schema for creating {resource}."""
    title: str
    description: Optional[str] = None
    # Add fields as needed

@dataclass
class {Resource}UpdateRequest:
    """Schema for updating {resource}."""
    title: Optional[str] = None
    description: Optional[str] = None
    # All fields optional for PATCH

@dataclass
class {Resource}Response:
    """Schema for {resource} response."""
    id: int
    title: str
    description: Optional[str]
    user_id: int
    created_at: str
    updated_at: str

@dataclass
class {Resource}ListResponse:
    """Schema for {resource} list response."""
    items: List[{Resource}Response]
    total: int
    page: int
    page_size: int
```

## Model Template

```python
# src/app/models/{resource}.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey
from datetime import datetime
from app.models import Base

class {Resource}(Base):
    __tablename__ = '{resource}s'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign key
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="{resource}s")

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

When generating, replace `{resource}` and `{Resource}` with actual names!
