---
description: Run mypy type checking on the codebase
argument-hint: [path]
allowed-tools: Bash(*)
model: haiku
---

Run mypy type checker to verify type annotations and catch type-related bugs.

Arguments:
- $1: Optional path to check (default: src/ directory)

Execute type checking:

```bash
cd tkinter-template
uv run mypy $1
```

If no path specified, check all source code:

```bash
cd tkinter-template
uv run mypy src/
```

The type checker will:
- Verify type annotations are correct
- Catch type mismatches
- Identify potential None errors
- Check function signatures
- Validate return types

If type errors are found:
1. Show the specific file and line number
2. Explain the type mismatch
3. Suggest corrections with proper type annotations
4. Offer to fix common type issues
