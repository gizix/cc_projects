---
description: Generate a new Tkinter view component with MVC pattern
argument-hint: <view-name>
model: sonnet
---

Create a new view component following the MVC pattern used in this template.

Arguments:
- $1: View name in PascalCase (e.g., `UserProfile`, `SettingsPanel`)

The view should:

1. **File Location**: Create `src/tkinter_app/views/<snake_case_name>_view.py`

2. **Class Structure**:
```python
"""<Description> view."""

import tkinter as tk
from typing import TYPE_CHECKING

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if TYPE_CHECKING:
    from tkinter_app.controllers.<controller_name> import <ControllerName>


class <ViewName>View(ttk.Frame):
    """<Description> view component."""

    def __init__(self, parent: tk.Widget, controller: "<ControllerName>") -> None:
        """Initialize view.

        Args:
            parent: Parent widget
            controller: Controller instance
        """
        super().__init__(parent)
        self.controller = controller
        self._build_ui()

    def _build_ui(self) -> None:
        """Build user interface."""
        # Add UI components here
        pass
```

3. **Best Practices**:
   - Use ttkbootstrap widgets (ttk.Button, ttk.Entry, etc.)
   - Separate UI building into `_build_ui()` method
   - Store widget references as instance attributes if needed later
   - Use TYPE_CHECKING to avoid circular imports
   - Add type hints to all methods
   - Include docstrings

4. **Update __init__.py**: Add the new view to `src/tkinter_app/views/__init__.py`

5. **Integration**: Show how to integrate with existing controller or suggest creating a new controller

Generate the complete view component with $1 as the name.
