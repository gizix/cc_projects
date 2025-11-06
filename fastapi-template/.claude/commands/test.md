---
description: Run tests with pytest and display coverage
argument-hint: [test-path] [--verbose]
---

Run the project's test suite using pytest with coverage reporting.

Execute:
```bash
uv run pytest $ARGUMENTS
```

Common usage patterns:
- `/test` - Run all tests with coverage
- `/test tests/test_api/` - Run specific test directory
- `/test -v` - Run with verbose output
- `/test --cov-report=html` - Generate HTML coverage report
