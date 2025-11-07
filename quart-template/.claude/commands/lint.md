---
description: Run Ruff + Black + Mypy
---

Run code quality tools: Ruff (linter), Black (formatter), and Mypy (type checker).

Execute the following commands:

```bash
cd quart-template

# Run Ruff linter (checks for errors and style issues)
ruff check src/ tests/

# Auto-fix Ruff issues where possible
ruff check src/ tests/ --fix

# Run Black formatter (formats code)
black src/ tests/

# Run Mypy type checker
mypy src/
```

Combined one-liner to run all checks:
```bash
cd quart-template && ruff check src/ tests/ --fix && black src/ tests/ && mypy src/
```

Expected output:
- Ruff: Lists any code quality issues and applies fixes
- Black: Reformats files if needed
- Mypy: Reports type errors if any

Configuration is in pyproject.toml.
