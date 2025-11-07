"""API blueprint for item management.

This blueprint demonstrates RESTful CRUD operations with authentication,
pagination, and validation.
"""

from quart import Blueprint, request
from quart_schema import validate_request, validate_response, validate_querystring, tag
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from ...models import get_session, Item
from ...schemas import (
    ItemCreateSchema,
    ItemUpdateSchema,
    ItemSchema,
    PaginatedItemsSchema,
    ErrorSchema,
)
from ...auth import require_auth, optional_auth

api_bp = Blueprint("api", __name__)


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


@api_bp.route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint.

    Returns API status and version information.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Quart API is running",
    }, 200


@api_bp.route("/items", methods=["GET"])
@tag(["items"])
@validate_querystring(PaginationParams)
@validate_response(PaginatedItemsSchema, 200)
@optional_auth
async def list_items(query_args: PaginationParams):
    """List all items with pagination.

    Supports pagination through query parameters.
    Authentication is optional - authenticated users see all items,
    unauthenticated users see only available items.
    """
    async with get_session() as session:
        # Build query
        query = select(Item)

        # Filter by availability for unauthenticated users
        from quart import g

        if not g.current_user:
            query = query.where(Item.is_available == True)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        result = await session.execute(count_query)
        total = result.scalar()

        # Apply pagination
        offset = (query_args.page - 1) * query_args.page_size
        query = query.limit(query_args.page_size).offset(offset)

        # Execute query
        result = await session.execute(query)
        items = result.scalars().all()

        # Calculate total pages
        total_pages = (total + query_args.page_size - 1) // query_args.page_size

        return {
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": query_args.page,
            "page_size": query_args.page_size,
            "total_pages": total_pages,
        }, 200


@api_bp.route("/items/<int:item_id>", methods=["GET"])
@tag(["items"])
@validate_response(ItemSchema, 200)
@validate_response(ErrorSchema, 404)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    async with get_session() as session:
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            return {"error": "Not Found", "message": f"Item {item_id} not found"}, 404

        return item.to_dict(), 200


@api_bp.route("/items", methods=["POST"])
@tag(["items"])
@require_auth
@validate_request(ItemCreateSchema)
@validate_response(ItemSchema, 201)
@validate_response(ErrorSchema, 400)
async def create_item(data: ItemCreateSchema):
    """Create a new item.

    Requires authentication. Creates a new item with the provided data.
    """
    async with get_session() as session:
        item = Item(
            name=data.name,
            description=data.description,
            price=data.price,
            is_available=data.is_available,
        )

        session.add(item)
        await session.commit()
        await session.refresh(item)

        return item.to_dict(), 201


@api_bp.route("/items/<int:item_id>", methods=["PUT"])
@tag(["items"])
@require_auth
@validate_request(ItemUpdateSchema)
@validate_response(ItemSchema, 200)
@validate_response(ErrorSchema, 404)
async def update_item(item_id: int, data: ItemUpdateSchema):
    """Update an existing item.

    Requires authentication. Updates item fields with provided data.
    Only provided fields are updated.
    """
    async with get_session() as session:
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            return {"error": "Not Found", "message": f"Item {item_id} not found"}, 404

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await session.commit()
        await session.refresh(item)

        return item.to_dict(), 200


@api_bp.route("/items/<int:item_id>", methods=["DELETE"])
@tag(["items"])
@require_auth
@validate_response(None, 204)
@validate_response(ErrorSchema, 404)
async def delete_item(item_id: int):
    """Delete an item.

    Requires authentication. Permanently deletes the specified item.
    """
    async with get_session() as session:
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            return {"error": "Not Found", "message": f"Item {item_id} not found"}, 404

        await session.delete(item)
        await session.commit()

        return "", 204
