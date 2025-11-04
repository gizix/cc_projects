---
description: Generate a modal dialog window component
argument-hint: <dialog-name>
model: sonnet
---

Create a new modal dialog window following the patterns in this template.

Arguments:
- $1: Dialog name in PascalCase (e.g., `ConfirmDelete`, `UserInput`)

The dialog should:

1. **File Location**: Create `src/tkinter_app/views/dialogs/<snake_case_name>_dialog.py`

2. **Class Structure**:
```python
"""<Description> dialog."""

import tkinter as tk
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class <DialogName>Dialog(tk.Toplevel):
    """Modal <description> dialog."""

    def __init__(self, parent: tk.Tk, **kwargs) -> None:
        """Initialize dialog.

        Args:
            parent: Parent window
            **kwargs: Dialog-specific parameters
        """
        super().__init__(parent)
        self.title("<Dialog Title>")
        self.result: Any | None = None

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._build_ui()

        # Center on parent
        self._center_on_parent(parent)

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def _build_ui(self) -> None:
        """Build dialog UI."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Add dialog content here

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=BOTTOM, fill=X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="OK",
            command=self.on_ok,
            bootstyle=PRIMARY,
        ).pack(side=RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
        ).pack(side=RIGHT)

    def _center_on_parent(self, parent: tk.Tk) -> None:
        """Center dialog on parent window."""
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        dialog_w = self.winfo_width()
        dialog_h = self.winfo_height()
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        self.geometry(f"+{x}+{y}")

    def on_ok(self) -> None:
        """Handle OK button."""
        self.result = self.get_result()
        self.destroy()

    def on_cancel(self) -> None:
        """Handle Cancel button."""
        self.result = None
        self.destroy()

    def get_result(self) -> Any:
        """Get dialog result."""
        # Return dialog data
        return {}

    @staticmethod
    def show_dialog(parent: tk.Tk, **kwargs) -> Any | None:
        """Show dialog and return result."""
        dialog = <DialogName>Dialog(parent, **kwargs)
        parent.wait_window(dialog)
        return dialog.result
```

3. **Features to Include**:
   - Modal behavior (transient + grab_set)
   - Centered on parent window
   - OK/Cancel buttons with proper styling
   - Static `show_dialog()` method for easy usage
   - Result storage and return
   - Window close handling

4. **Update __init__.py**: Add dialog to `src/tkinter_app/views/dialogs/__init__.py`

Generate the complete dialog component with $1 as the name.
