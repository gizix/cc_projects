"""Main application view."""

import tkinter as tk
from typing import TYPE_CHECKING, Callable
from uuid import UUID

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from tkinter_app.models import TodoItem

if TYPE_CHECKING:
    from tkinter_app.controllers.main_controller import MainController


class MainView(ttk.Frame):
    """Main application view with todo list."""

    def __init__(self, parent: tk.Widget, controller: "MainController") -> None:
        """Initialize main view.

        Args:
            parent: Parent widget
            controller: Main controller
        """
        super().__init__(parent)
        self.controller = controller
        self._build_ui()

    def _build_ui(self) -> None:
        """Build user interface."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=X, padx=20, pady=(20, 10))

        title = ttk.Label(
            title_frame,
            text="Todo List",
            font=("Segoe UI", 24, "bold"),
        )
        title.pack(side=LEFT)

        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=X, padx=20, pady=10)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Segoe UI", 11),
        )
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self.controller.on_add_item())

        self.add_button = ttk.Button(
            input_frame,
            text="Add",
            command=self.controller.on_add_item,
            bootstyle=PRIMARY,
        )
        self.add_button.pack(side=RIGHT)

        # List frame with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Listbox for todos
        self.listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            activestyle="none",
        )
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Double-click to toggle
        self.listbox.bind("<Double-Button-1>", lambda e: self.controller.on_toggle_item())

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, padx=20, pady=(0, 20))

        self.toggle_button = ttk.Button(
            button_frame,
            text="Toggle Complete",
            command=self.controller.on_toggle_item,
            bootstyle=INFO,
        )
        self.toggle_button.pack(side=LEFT, padx=(0, 5))

        self.delete_button = ttk.Button(
            button_frame,
            text="Delete",
            command=self.controller.on_delete_item,
            bootstyle=DANGER,
        )
        self.delete_button.pack(side=LEFT, padx=5)

        self.clear_completed_button = ttk.Button(
            button_frame,
            text="Clear Completed",
            command=self.controller.on_clear_completed,
            bootstyle=WARNING,
        )
        self.clear_completed_button.pack(side=LEFT, padx=5)

        # Status label
        self.status_label = ttk.Label(
            button_frame,
            text="",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side=RIGHT)

    def get_input_text(self) -> str:
        """Get input entry text.

        Returns:
            Input text
        """
        return self.input_var.get()

    def clear_input(self) -> None:
        """Clear input entry."""
        self.input_var.set("")

    def get_selected_item_id(self) -> UUID | None:
        """Get selected item ID.

        Returns:
            UUID of selected item or None
        """
        selection = self.listbox.curselection()
        if not selection:
            return None

        index = selection[0]
        # Get UUID from listbox item data
        return self.listbox.get(index)

    def update_list(self, items: list[TodoItem]) -> None:
        """Update listbox with items.

        Args:
            items: List of todo items
        """
        # Store current selection
        selected = self.listbox.curselection()
        selected_index = selected[0] if selected else None

        # Clear listbox
        self.listbox.delete(0, tk.END)

        # Add items
        for item in items:
            status = "" if item.completed else "Ë"
            text = f"{status} {item.title}"
            self.listbox.insert(tk.END, text)

            # Store UUID as internal data
            # We'll use a mapping in controller instead
            if item.completed:
                self.listbox.itemconfig(tk.END, fg="gray")

        # Restore selection
        if selected_index is not None and selected_index < self.listbox.size():
            self.listbox.selection_set(selected_index)

        # Update status
        active_count = len([item for item in items if not item.completed])
        total_count = len(items)
        self.status_label.config(text=f"{active_count} active / {total_count} total")

    def show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message
        """
        from tkinter import messagebox

        messagebox.showerror("Error", message)

    def show_info(self, message: str) -> None:
        """Show info message.

        Args:
            message: Info message
        """
        from tkinter import messagebox

        messagebox.showinfo("Info", message)

    def focus_input(self) -> None:
        """Focus input entry."""
        self.input_entry.focus()
