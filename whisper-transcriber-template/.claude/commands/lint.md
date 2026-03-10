---
description: Run ruff linter on all Python source files
---

Run the ruff linter to check for code quality issues.

Execute: `uv run ruff check src/ tests/`

After running:
- If no issues found, confirm the code is clean
- If issues are found, show them and ask if the user wants them auto-fixed
- To auto-fix: `uv run ruff check --fix src/ tests/`

Common issues ruff catches:
- Unused imports
- Undefined variables
- Style violations (PEP 8)
- Simplifiable expressions
