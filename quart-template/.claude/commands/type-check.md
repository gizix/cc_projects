---
description: Run mypy type checker
allowed-tools: Bash(*)
model: sonnet
---

Perform static type checking using mypy to catch type-related errors before runtime.

## Usage

```bash
/type-check
```

## What This Does

Analyzes code for:
- Type annotation errors
- Incompatible type assignments
- Missing return types
- Incorrect async/await usage
- Generic type issues
- Optional/None handling errors

## Command

```bash
echo "Running mypy type checker..."
mypy src
```

## Benefits for Async Code

Especially important for Quart applications:
- Validates async function returns
- Checks proper await usage
- Verifies async context manager types
- Catches coroutine/future confusion
- Ensures correct async session types

## Type Checking Standards

Expected in this project:
- All function signatures typed
- Return types specified
- No `Any` types (except unavoidable)
- Strict optional checking enabled
- Async types properly annotated

## Example Annotations

```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(
    session: AsyncSession,
    user_id: int
) -> Optional[User]:
    ...
```

## Notes

- Configuration in `pyproject.toml`
- Incremental mode for fast re-checking
- Can be strict or gradual
- Integrate with CI/CD pipeline
