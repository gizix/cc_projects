---
description: Generate SQLAlchemy model with async patterns
argument-hint: <model_name>
allowed-tools: Read, Write, Grep
model: sonnet
---

Create a new SQLAlchemy model using modern SQLAlchemy 2.0+ patterns with proper async support.

## Arguments

- `$1`: Model name in PascalCase (e.g., "Post", "Comment", "Product")

## Usage

```bash
/create-model Post
/create-model Comment
/create-model Product
```

## What This Creates

**Model File** (`src/app/models/{name_lower}.py`):
- SQLAlchemy 2.0 model with `Mapped` annotations
- Primary key field (id)
- Timestamp fields (created_at, updated_at)
- Example fields with proper types
- Indexes for common queries
- Relationship examples

## Generated Model Example

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey, Index
from datetime import datetime
from app.models import Base

class {Name}(Base):
    __tablename__ = "{name_plural}"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Example fields (customize as needed)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign key example
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship example
    # user: Mapped["User"] = relationship(back_populates="{name_plural}")

    # Composite index example
    # __table_args__ = (
    #     Index('ix_{name_lower}_user_created', 'user_id', 'created_at'),
    # )

    def __repr__(self) -> str:
        return f"<{Name}(id={self.id}, title={self.title})>"
```

## SQLAlchemy 2.0 Features

- **Mapped Type Annotations**: Clear type hints for all columns
- **Type Safety**: Better IDE autocomplete and type checking
- **Modern Syntax**: Follows latest SQLAlchemy best practices
- **Async Ready**: Works seamlessly with async sessions

## Next Steps After Generation

1. Customize fields for your use case
2. Add relationships to other models
3. Create indexes for query optimization
4. Generate migration with `/db-migrate "add {name} table"`
5. Apply migration with `/db-upgrade`
6. Create corresponding routes with `/create-route`

## Common Field Types

```python
# String fields
name: Mapped[str] = mapped_column(String(100))
email: Mapped[str] = mapped_column(String(120), unique=True)

# Optional fields
bio: Mapped[str | None] = mapped_column(Text, nullable=True)

# Integer fields
age: Mapped[int] = mapped_column(Integer)
count: Mapped[int] = mapped_column(default=0)

# Boolean fields
is_active: Mapped[bool] = mapped_column(default=True)

# DateTime fields
published_at: Mapped[datetime | None] = mapped_column(nullable=True)
```

## Notes

- Model name should be singular (Post, not Posts)
- Table name will be pluralized automatically
- Includes common timestamps by default
- Relationship examples commented out
- Add to Alembic env.py imports if needed
