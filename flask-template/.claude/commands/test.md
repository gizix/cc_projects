---
description: Run pytest test suite
argument-hint: "[TEST_PATH] [OPTIONS]"
---

Run the test suite using pytest.

## Arguments

- `TEST_PATH` (optional): Specific test file or directory to run
- `OPTIONS`: Additional pytest options

## Common Options

- `-v` or `--verbose`: Verbose output
- `-s`: Show print statements
- `-x`: Stop on first failure
- `--lf`: Run last failed tests
- `--cov`: Show coverage report
- `--cov-report=html`: Generate HTML coverage report
- `-k PATTERN`: Run tests matching pattern

## Examples

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestAuthEndpoints

# Run specific test
pytest tests/test_api.py::TestAuthEndpoints::test_login_success

# Run tests matching pattern
pytest -k "auth"

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Stop on first failure
pytest -x

# Run last failed tests only
pytest --lf
```

## Notes

- Tests use in-memory SQLite database
- Each test runs in isolated transaction
- Fixtures defined in `tests/conftest.py`
- Coverage reports help identify untested code

Execute: `cd flask-template && pytest $ARGUMENTS`
