---
description: Run Ruff linter to check code quality
argument-hint: [--fix]
allowed-tools: Bash(*)
model: sonnet
---

Check code for style issues, errors, and potential bugs using Ruff linter.

## Arguments

- `$1`: `--fix` to automatically fix issues (optional)

## Usage

- `/lint` - Check code and report issues
- `/lint --fix` - Check and automatically fix issues

## What This Does

Ruff checks for:
- PEP 8 style violations
- Common Python errors
- Security issues (e.g., SQL injection patterns)
- Unused imports and variables
- Complexity issues
- Async/await pattern errors
- Type annotation issues

## Command

```bash
if [ "$1" = "--fix" ]; then
    echo "Running Ruff with auto-fix..."
    ruff check src tests --fix
else
    echo "Running Ruff linter..."
    ruff check src tests
fi
```

## Ruff Rules Enabled

- `E` - pycodestyle errors
- `F` - Pyflakes
- `I` - isort (import sorting)
- `N` - pep8-naming
- `W` - pycodestyle warnings
- `S` - flake8-bandit (security)
- `B` - flake8-bugbear
- `ASYNC` - async/await issues

## Notes

- Auto-fix is safe and non-destructive
- Manual review recommended after auto-fix
- Some issues require manual intervention
- Configuration in `pyproject.toml`
