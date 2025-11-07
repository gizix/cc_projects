---
description: Run pytest suite with coverage
---

Run the test suite using pytest with coverage reporting.

Execute the following command:

```bash
cd quart-template && pytest tests/ -v --cov=src/app --cov-report=term-missing --cov-report=html
```

This will:
- Run all tests in the tests/ directory
- Show verbose output (-v)
- Generate coverage report for src/app
- Display missing lines in terminal
- Create HTML coverage report in htmlcov/

To run specific tests:
```bash
pytest tests/test_api.py::TestAuthentication -v
```

To run tests and stop on first failure:
```bash
pytest tests/ -x
```
