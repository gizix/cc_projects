---
description: Format all Python source files with ruff formatter
---

Format all Python source files using ruff.

Execute: `uv run ruff format src/ tests/`

After running:
- Show how many files were reformatted
- Confirm all files follow the project's style (100 char line length, double quotes)

Note: The PostToolUse hook auto-formats files after Claude edits them. Run this command to format files you've edited manually.
