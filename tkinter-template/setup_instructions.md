# Tkinter Template Setup Instructions

Step-by-step guide to set up and start using this Tkinter application template.

## Prerequisites

### 1. Install Python 3.13+

**Windows:**
```powershell
# Download from python.org or use winget
winget install Python.Python.3.13
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.13
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3.13-venv python3-tk

# Fedora
sudo dnf install python3.13 python3-tkinter
```

### 2. Install uv Package Manager

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

## Setup Steps

### 1. Navigate to Template Directory

```bash
cd tkinter-template
```

### 2. Install Dependencies

```bash
# Install all dependencies
uv sync

# Install including dev dependencies (for testing, building)
uv sync --dev
```

This creates a virtual environment and installs:
- ttkbootstrap (modern Tkinter themes)
- pillow (image handling)
- platformdirs (cross-platform paths)
- loguru (logging)
- python-dotenv (environment variables)
- pytest (testing)
- mypy (type checking)
- ruff (linting/formatting)
- pyinstaller (executable building)

### 3. Configure Environment (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your preferences
# APP_NAME, LOG_LEVEL, DEFAULT_THEME, etc.
```

### 4. Verify Installation

```bash
# Run the application
uv run python -m tkinter_app
```

You should see the todo list application window open.

### 5. Run Tests

```bash
# Run test suite
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py
```

### 6. Verify Code Quality Tools

```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## Using with Claude Code

### 1. Open in VSCode

```bash
# Open the template directory in VSCode
code .
```

### 2. Launch Claude Code

- Press `Ctrl+L` (Windows/Linux) or `Cmd+L` (macOS)
- Or click Claude Code icon in sidebar

### 3. Explore Available Commands

Type `/help` in Claude Code to see all available commands:

```
/dev - Run application
/test - Run tests
/format - Format code
/lint - Lint code
/new-view <name> - Generate view
/new-dialog <name> - Generate dialog
/new-model <name> - Generate model
```

### 4. Ask Claude Code for Help

Claude Code has specialized knowledge about this template:

- "Create a new user registration form"
- "Add validation to the email field"
- "How do I create a modal dialog?"
- "Help me implement a background task"

## Customizing the Template

### 1. Rename the Application

1. Update `pyproject.toml`:
   ```toml
   [project]
   name = "your-app-name"
   ```

2. Rename package directory:
   ```bash
   mv src/tkinter_app src/your_app_name
   ```

3. Update imports throughout the codebase

4. Update `.env` file:
   ```
   APP_NAME=YourAppName
   ```

### 2. Change Default Theme

Edit `src/tkinter_app/resources/config/default_settings.json`:

```json
{
  "theme": "darkly"
}
```

Available themes:
- Light: cosmo, flatly, litera, minty, pulse, sandstone
- Dark: darkly, solar, superhero, vapor

### 3. Add Custom Icon

1. Add your icon to `src/tkinter_app/resources/images/icon.png`
2. The app automatically loads it if present

### 4. Modify Window Settings

Edit default settings:

```json
{
  "window_size": {
    "width": 1024,
    "height": 768
  },
  "font_family": "Segoe UI",
  "font_size": 11
}
```

## Development Workflow

### Day-to-Day Development

```bash
# 1. Run application
uv run python -m tkinter_app

# 2. Make changes to code

# 3. Format and lint
uv run ruff format .
uv run ruff check --fix .

# 4. Run tests
uv run pytest

# 5. Type check
uv run mypy src/
```

### Creating New Features

1. **Plan the feature** with Claude Code
2. **Create model** using `/new-model <name>`
3. **Create view** using `/new-view <name>`
4. **Create controller** (or use mvc-pattern skill)
5. **Add tests** for new components
6. **Integrate** into main app

### Before Committing

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Run tests
uv run pytest

# Type check
uv run mypy src/
```

## Building for Distribution

### Create Executable

```bash
# Build single-file executable
uv run python scripts/build.py
```

Output location:
- Windows: `dist/TkinterApp.exe`
- macOS: `dist/TkinterApp.app`
- Linux: `dist/TkinterApp`

### Test Executable

```bash
# Run the built executable
./dist/TkinterApp  # Linux/macOS
dist\TkinterApp.exe  # Windows
```

Test on a clean system without Python installed.

### Distribution Checklist

- [ ] All features working in executable
- [ ] Resources (images, themes) bundled correctly
- [ ] Configuration loads from correct location
- [ ] No console window appears (Windows, with --windowed flag)
- [ ] Application icon displays correctly
- [ ] File size is reasonable
- [ ] Tested on target operating system

## Troubleshooting

### uv sync fails

**Problem:** Dependencies fail to install

**Solutions:**
```bash
# Clear cache and retry
uv cache clean
uv sync

# Check Python version
python --version  # Should be 3.13+

# Update uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Application won't start

**Problem:** Display errors or import errors

**Solutions:**
```bash
# Linux: Install tkinter
sudo apt install python3-tk

# Linux: Use virtual display
xvfb-run uv run python -m tkinter_app

# All: Check dependencies
uv sync
```

### Tests fail

**Problem:** pytest errors

**Solutions:**
```bash
# Install dev dependencies
uv sync --dev

# Run tests with verbose output
uv run pytest -v

# Check specific test
uv run pytest tests/test_models.py::test_name -v
```

### Build fails

**Problem:** PyInstaller errors

**Solutions:**
```bash
# Install PyInstaller
uv sync --dev

# Clean previous builds
rm -rf build/ dist/

# Run build again
uv run python scripts/build.py

# Check for hidden import issues
# Add to build.py: --hidden-import=module_name
```

## Next Steps

1. **Read CLAUDE.md** - Comprehensive context for Claude Code
2. **Explore example app** - Study the todo list implementation
3. **Try commands** - Use `/new-view`, `/new-model`, etc.
4. **Build your app** - Replace todo list with your feature
5. **Test thoroughly** - Write tests for new components
6. **Build executable** - Create distributable app

## Getting Help

- **Claude Code**: Ask questions directly in Claude Code
- **Documentation**: See README.md and CLAUDE.md
- **Example Code**: Study files in src/tkinter_app/
- **Commands**: Type `/help` in Claude Code

Happy coding! =€
