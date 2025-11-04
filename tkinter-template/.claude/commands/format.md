---
description: Format Python code with ruff
argument-hint: [path]
allowed-tools: Bash(*)
model: haiku
---

Format Python code using ruff formatter.

Arguments:
- $1: Optional path to format (default: entire src/ and tests/ directories)

Execute formatting:

```bash
cd tkinter-template
uv run ruff format $1
```

If no path specified, format all code:

```bash
cd tkinter-template
uv run ruff format src/ tests/
```

The formatter will:
- Apply consistent code style
- Fix line lengths
- Organize imports
- Apply PEP 8 formatting rules

This command modifies files in-place. All changes should be reviewed before committing.
