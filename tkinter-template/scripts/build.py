#!/usr/bin/env python3
"""Build executable with PyInstaller."""

import subprocess
import sys
from pathlib import Path


def build() -> None:
    """Build executable using PyInstaller."""
    print("Building Tkinter App executable...")
    print("-" * 50)

    # Get project root
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    main_file = src_dir / "tkinter_app" / "__main__.py"

    if not main_file.exists():
        print(f"Error: Main file not found: {main_file}")
        sys.exit(1)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=TkinterApp",
        "--windowed",  # No console window
        "--onefile",  # Single executable
        "--clean",  # Clean cache
        "--noconfirm",  # Overwrite without asking
        f"--add-data={src_dir / 'tkinter_app' / 'resources'}{';' if sys.platform == 'win32' else ':'}tkinter_app/resources",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=PIL._tkinter_finder",
        str(main_file),
    ]

    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print(" Build successful!")
        print("=" * 50)

        # Show output location
        exe_name = "TkinterApp.exe" if sys.platform == "win32" else "TkinterApp"
        exe_path = project_root / "dist" / exe_name
        print(f"\nExecutable location: {exe_path}")

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Size: {size_mb:.1f} MB")
    else:
        print("\n" + "=" * 50)
        print(" Build failed")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    build()
