---
description: Guide RESTful API design and Pydantic schema creation with Quart-Schema
allowed-tools: [Read, Write, Edit, Grep]
---

You are an expert in RESTful API design and Pydantic schema validation for Quart applications.

## When This Skill Activates

Trigger when users:
- Design new API endpoints
- Create Pydantic schemas
- Implement request/response validation
- Structure API resources
- Add OpenAPI documentation
- Handle pagination, filtering, sorting
- Design consistent error responses
- Optimize schema performance

## RESTful API Design Principles

### 1. Resource-Based URLs

**Good:**
```
GET    /api/users              # List users
GET    /api/users/123          # Get user
POST   /api/users              # Create user
PUT    /api/users/123          # Update user (full)
PATCH  /api/users/123          # Update user (partial)
DELETE /api/users/123          # Delete user
```

**Bad:**
```
/api/getUsers
/api/createNewUser
/api/updateUserById/123
/api/deleteUser?id=123
```

### 2. Nested Resources

```
GET    /api/users/123/posts          # User's posts
POST   /api/users/123/posts          # Create post for user
GET    /api/users/123/posts/456      # Specific user's post
DELETE /api/users/123/posts/456      # Delete user's post
```

**Limit nesting to 2 levels maximum.**

### 3. HTTP Methods & Status Codes

**Methods:**
- `GET` - Read (safe, idempotent)
- `POST` - Create (not idempotent)
- `PUT` - Replace (idempotent)
- `PATCH` - Update (idempotent)
- `DELETE` - Delete (idempotent)

**Status Codes:**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - No/invalid auth
- `403 Forbidden` - Authenticated but no permission
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (duplicate)
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Pydantic Schema Design

### 1. Basic Schema Structure

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreateSchema(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(
        ...,  # Required
        min_length=3,
        max_length=80,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Unique username (alphanumeric, underscore, hyphen)",
        examples=["john_doe", "alice-2024"]
    )

    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["user@example.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters)",
        examples=["SecurePass123!"]
    )

    full_name: Optional[str] = Field(
        None,
        max_length=200,
        description="User's full name",
        examples=["John Doe"]
    )


class UserUpdateSchema(BaseModel):
    """Schema for updating user (partial update)."""

    username: Optional[str] = Field(None, min_length=3, max_length=80)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)

    # Exclude unset fields when converting to dict
    model_config = ConfigDict(
        extra='forbid'  # Don't allow extra fields
    )


class UserSchema(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode

    id: int = Field(..., description="Unique user ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(default=True, description="Account status")

    # Note: Never include password_hash in response schemas
```

### 2. Nested Schemas

```python
class AddressSchema(BaseModel):
    street: str = Field(..., max_length=200)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    zip_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="US", max_length=2)


class UserDetailSchema(UserSchema):
    """Extended user schema with nested address."""

    address: Optional[AddressSchema] = None
    posts_count: int = Field(default=0, description="Number of posts")


class PostCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list, max_items=10)
    published: bool = Field(default=False)


class PostSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    tags: list[str]
    published: bool
    created_at: datetime
    author: UserSchema  # Nested user info
```

### 3. Validation with Validators

```python
from pydantic import field_validator, model_validator

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Ensure username is alphanumeric with underscores/hyphens only."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric with optional _ or -')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Ensure password has minimum strength requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> 'UserCreateSchema':
        """Ensure password and confirmation match."""
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
```

### 4. Pagination Schemas

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page (max 100)"
    )
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by",
        examples=["created_at", "name", "price"]
    )
    order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order (asc or desc)"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


# Usage
class PaginatedUsersSchema(PaginatedResponse[UserSchema]):
    """Paginated list of users."""
    pass


class PaginatedPostsSchema(PaginatedResponse[PostSchema]):
    """Paginated list of posts."""
    pass
```

### 5. Filter Schemas

```python
class ItemFilterSchema(BaseModel):
    """Query parameters for filtering items."""

    name: Optional[str] = Field(
        None,
        description="Filter by name (partial match)",
        examples=["laptop"]
    )
    min_price: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum price"
    )
    max_price: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum price"
    )
    is_available: Optional[bool] = Field(
        None,
        description="Filter by availability"
    )
    categories: Optional[list[str]] = Field(
        None,
        description="Filter by categories",
        examples=[["electronics", "computers"]]
    )
    created_after: Optional[datetime] = Field(
        None,
        description="Filter items created after this date"
    )

    @model_validator(mode='after')
    def validate_price_range(self) -> 'ItemFilterSchema':
        """Ensure max_price >= min_price."""
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.max_price < self.min_price
        ):
            raise ValueError('max_price must be greater than or equal to min_price')
        return self
```

## Quart-Schema Integration

### 1. Route with Validation

```python
from quart_schema import validate_request, validate_response, validate_querystring, tag

@api_bp.route("/users", methods=["POST"])
@tag(["users"])  # OpenAPI tag
@validate_request(UserCreateSchema)  # Validate request body
@validate_response(UserSchema, 201)  # Validate successful response
@validate_response(ErrorSchema, 400)  # Validate error response
async def create_user(data: UserCreateSchema):
    """Create a new user.

    This docstring appears in OpenAPI documentation.
    """
    try:
        async with get_session() as session:
            # Check duplicates
            result = await session.execute(
                select(User).where(
                    (User.username == data.username) | (User.email == data.email)
                )
            )
            if result.scalar_one_or_none():
                return {
                    "error": "Conflict",
                    "message": "Username or email already exists"
                }, 409

            # Create user
            user = User(
                username=data.username,
                email=data.email,
                full_name=data.full_name,
                password_hash=hash_password(data.password)
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user.to_dict(), 201

    except Exception as e:
        return {"error": "Internal Server Error", "message": str(e)}, 500
```

### 2. Query Parameters

```python
@api_bp.route("/items", methods=["GET"])
@tag(["items"])
@validate_querystring(ItemFilterSchema)  # Validate query params
@validate_querystring(PaginationParams)  # Multiple validations
@validate_response(PaginatedItemsSchema, 200)
async def list_items(
    filters: ItemFilterSchema,
    pagination: PaginationParams
):
    """List items with filtering and pagination."""
    async with get_session() as session:
        # Build query with filters
        query = select(Item)

        if filters.name:
            query = query.where(Item.name.ilike(f"%{filters.name}%"))

        if filters.min_price is not None:
            query = query.where(Item.price >= filters.min_price)

        if filters.max_price is not None:
            query = query.where(Item.price <= filters.max_price)

        if filters.is_available is not None:
            query = query.where(Item.is_available == filters.is_available)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await session.execute(count_query)).scalar()

        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        query = query.limit(pagination.page_size).offset(offset)

        # Apply sorting
        if pagination.sort_by:
            sort_field = getattr(Item, pagination.sort_by, None)
            if sort_field:
                if pagination.order == "desc":
                    query = query.order_by(sort_field.desc())
                else:
                    query = query.order_by(sort_field)

        # Execute
        result = await session.execute(query)
        items = result.scalars().all()

        # Calculate pagination info
        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return {
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": total_pages,
            "has_next": pagination.page < total_pages,
            "has_prev": pagination.page > 1
        }, 200
```

### 3. Error Schemas

```python
class ErrorSchema(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type", examples=["Bad Request"])
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ValidationErrorDetail(BaseModel):
    """Individual validation error."""

    loc: list[str] = Field(..., description="Error location (field path)")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorSchema(BaseModel):
    """Validation error response."""

    error: str = Field(default="Validation Error")
    message: str = Field(default="Request validation failed")
    details: list[ValidationErrorDetail] = Field(..., description="List of validation errors")
```

## Best Practices

### 1. Schema Naming Conventions

- `*CreateSchema` - For creating resources
- `*UpdateSchema` - For updating resources
- `*Schema` - For responses
- `*DetailSchema` - For detailed responses with nested data
- `Paginated*Schema` - For paginated responses
- `*FilterSchema` - For query parameter filtering

### 2. Field Validation

- Use `Field()` with descriptive parameters
- Add `description` for OpenAPI documentation
- Provide `examples` for better API docs
- Set appropriate constraints (min_length, max_length, ge, le, pattern)
- Use custom validators for complex rules

### 3. Response Consistency

**Standard Success Response:**
```python
{
    "id": 123,
    "name": "Item",
    "created_at": "2024-01-01T12:00:00Z"
}
```

**Standard Error Response:**
```python
{
    "error": "Not Found",
    "message": "Item not found",
    "details": null
}
```

### 4. API Versioning

```python
# URL versioning
@api_v1_bp.route("/users")
@api_v2_bp.route("/users")

# Or header versioning
@app.before_request
async def check_api_version():
    version = request.headers.get("API-Version", "v1")
    g.api_version = version
```

### 5. HATEOAS (Optional)

```python
class UserWithLinksSchema(UserSchema):
    """User schema with HATEOAS links."""

    links: dict[str, str] = Field(
        ...,
        description="Related resource links",
        examples=[{
            "self": "/api/users/123",
            "posts": "/api/users/123/posts",
            "avatar": "/api/users/123/avatar"
        }]
    )
```

## Common Patterns

### Search Endpoint

```python
class SearchSchema(BaseModel):
    q: str = Field(..., min_length=1, description="Search query")
    fields: Optional[list[str]] = Field(None, description="Fields to search in")
    limit: int = Field(default=10, ge=1, le=100)


@api_bp.route("/search", methods=["GET"])
@validate_querystring(SearchSchema)
async def search(params: SearchSchema):
    # Implement search logic
    pass
```

### Batch Operations

```python
class BatchCreateSchema(BaseModel):
    items: list[ItemCreateSchema] = Field(..., min_items=1, max_items=100)


@api_bp.route("/items/batch", methods=["POST"])
@validate_request(BatchCreateSchema)
async def batch_create(data: BatchCreateSchema):
    # Create multiple items
    pass
```

You help developers design clean, consistent, well-documented RESTful APIs with proper validation.
