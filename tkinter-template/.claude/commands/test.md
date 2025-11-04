---
description: Run the test suite with optional filters
argument-hint: [test-path] [options]
allowed-tools: Bash(*)
model: haiku
---

Run the project's test suite using pytest.

Arguments:
- $1: Optional test path or pattern (e.g., `tests/test_models.py`)
- $2+: Optional pytest flags (e.g., `--verbose`, `--coverage`, `-k pattern`)

Execute tests:

```bash
cd tkinter-template
uv run pytest $ARGUMENTS
```

Common usage patterns:
- `/test` - Run all tests
- `/test tests/test_models.py` - Run specific test file
- `/test -v` - Run with verbose output
- `/test -k "test_add"` - Run tests matching pattern
- `/test --cov=tkinter_app` - Run with coverage

If tests fail:
1. Show failure summary with file and line numbers
2. Identify the specific assertion or error
3. Suggest potential fixes based on the failure
4. Offer to run specific failing tests for debugging
