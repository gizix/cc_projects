---
description: Lint Python code with ruff check
argument-hint: [path]
allowed-tools: Bash(*)
model: haiku
---

Lint Python code using ruff linter to check for code quality issues.

Arguments:
- $1: Optional path to lint (default: entire src/ and tests/ directories)

Execute linting:

```bash
cd tkinter-template
uv run ruff check $1
```

If no path specified, lint all code:

```bash
cd tkinter-template
uv run ruff check src/ tests/
```

To automatically fix issues:

```bash
cd tkinter-template
uv run ruff check --fix $1
```

The linter checks for:
- Syntax errors
- Unused imports
- Undefined variables
- Code complexity issues
- Style violations
- Common anti-patterns

Review all auto-fixes before committing changes.
