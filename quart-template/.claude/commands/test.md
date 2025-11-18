---
description: Run pytest test suite with async support
argument-hint: [test_path]
allowed-tools: Bash(*)
model: sonnet
---

Execute the test suite using pytest with pytest-asyncio for async test support.

## Arguments

- `$ARGUMENTS`: Specific test path or pytest options (optional, runs all tests if omitted)

## Usage

- `/test` - Run all tests
- `/test tests/test_auth.py` - Run specific test file
- `/test tests/test_auth.py::test_login` - Run specific test
- `/test -v` - Run with verbose output
- `/test -k login` - Run tests matching "login"
- `/test -x` - Stop on first failure

## What This Does

1. Discovers all test files in `tests/` directory
2. Executes async tests using pytest-asyncio
3. Shows test results and coverage information
4. Reports failures with detailed tracebacks

## Command

```bash
pytest $ARGUMENTS
```

## Test Structure

Tests should follow pytest-asyncio patterns:

```python
import pytest

@pytest.mark.asyncio
async def test_example(client):
    response = await client.get('/api/endpoint')
    assert response.status_code == 200
```

## Notes

- All async tests must be marked with `@pytest.mark.asyncio`
- Use fixtures from `tests/conftest.py` for app and client
- Tests run in isolation with separate database state
- WebSocket tests use `app.test_client().websocket()`
