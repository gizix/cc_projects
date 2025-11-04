---
description: Run the Tkinter application in development mode
allowed-tools: Bash(*)
model: haiku
---

Run the Tkinter application in development mode using uv.

Execute the application with:

```bash
cd tkinter-template
uv run python -m tkinter_app
```

If the application fails to start:
1. Check if dependencies are installed: `uv sync`
2. Verify Python version: `python --version` (should be 3.13+)
3. Check for error messages in console
4. Ensure X11/display is available (Linux)

Common issues:
- Missing dependencies: Run `uv sync`
- Display issues on Linux: Set `DISPLAY` environment variable
- Theme not loading: Check ttkbootstrap installation
