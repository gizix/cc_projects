---
description: Format code with Ruff formatter
allowed-tools: Bash(*)
model: sonnet
---

Format all Python code using Ruff's formatter for consistent code style.

## Usage

```bash
/format
```

## What This Does

1. Formats all Python files in `src/` and `tests/`
2. Applies PEP 8 style guidelines
3. Normalizes quotes, spacing, and indentation
4. Sorts imports automatically
5. Wraps long lines appropriately

## Command

```bash
echo "Formatting code with Ruff..."
ruff format src tests
echo "Code formatting complete!"
```

## Style Applied

- Line length: 88 characters (Black-compatible)
- Double quotes for strings
- 4 spaces for indentation
- Sorted imports (stdlib, third-party, local)
- Trailing commas in multi-line structures
- Consistent blank lines

## Integration

This command is safe to run frequently:
- Before committing code
- After generating new files
- After major refactoring
- As part of pre-commit hooks

## Notes

- Non-destructive operation
- Works with Git to preserve changes
- Compatible with Ruff linter
- Fast execution (Rust-based)
