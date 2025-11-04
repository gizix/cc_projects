---
description: Build executable with PyInstaller
allowed-tools: Bash(*)
model: sonnet
---

Build a standalone executable using PyInstaller.

Execute the build script:

```bash
cd tkinter-template
uv run python scripts/build.py
```

This will:
1. Run PyInstaller with optimized settings
2. Bundle Python interpreter and dependencies
3. Include resource files (images, themes, config)
4. Create single-file executable in `dist/` directory

Build output location:
- Windows: `dist/TkinterApp.exe`
- macOS: `dist/TkinterApp.app`
- Linux: `dist/TkinterApp`

If build fails:
1. Check if PyInstaller is installed: `uv sync --dev`
2. Verify all dependencies are available
3. Check for missing resource files
4. Review PyInstaller warnings in output

After successful build:
- Test the executable thoroughly
- Check that all resources load correctly
- Verify themes and images are bundled
- Test on clean system without Python installed
