---
description: Open interactive Quart shell with app context
allowed-tools: Bash(*)
model: sonnet
---

Launch an interactive Python shell with the Quart application context loaded.

## What's Available in the Shell

- `app` - The Quart application instance
- `db` - Database session (if configured)
- All models imported automatically
- Access to all application utilities

## Usage

```bash
/shell
```

## What This Does

Opens an interactive Python REPL where you can:
- Test async functions
- Query the database
- Inspect application configuration
- Test utilities and helpers
- Debug application state

## Example Session

```python
>>> from app.models.user import User
>>> from sqlalchemy import select
>>> # Test async operations
>>> import asyncio
>>> async def get_users():
...     async with async_session() as session:
...         result = await session.execute(select(User))
...         return result.scalars().all()
>>> users = asyncio.run(get_users())
>>> print(users)
```

## Command

```bash
python -c "from src.app import create_app; app = create_app(); import code; code.interact(local=locals())"
```

## Notes

- Use `asyncio.run()` to execute async functions
- Exit with Ctrl+D or `exit()`
- Changes made in shell are not persisted unless committed
