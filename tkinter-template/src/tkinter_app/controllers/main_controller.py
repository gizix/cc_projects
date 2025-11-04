"""Main application controller."""

import tkinter as tk
from typing import TYPE_CHECKING

from loguru import logger

from tkinter_app.models import TodoModel

if TYPE_CHECKING:
    from tkinter_app.views.main_view import MainView


class MainController:
    """Controller connecting model and view."""

    def __init__(self, root: tk.Tk, model: TodoModel) -> None:
        """Initialize controller.

        Args:
            root: Root window
            model: Todo model
        """
        self.root = root
        self.model = model
        self.view: "MainView | None" = None
        self._item_id_map: dict[int, str] = {}  # Listbox index to UUID mapping

        # Subscribe to model changes
        self.model.add_observer(self._on_model_changed)
        logger.debug("MainController initialized")

    def set_view(self, view: "MainView") -> None:
        """Set view reference.

        Args:
            view: Main view
        """
        self.view = view
        self._update_view()

    def _on_model_changed(self) -> None:
        """Handle model changes."""
        self._update_view()

    def _update_view(self) -> None:
        """Update view with current model data."""
        if self.view:
            items = self.model.get_all_items()
            self.view.update_list(items)

            # Update ID mapping
            self._item_id_map = {i: str(item.id) for i, item in enumerate(items)}

    def on_add_item(self) -> None:
        """Handle add item action."""
        if not self.view:
            return

        title = self.view.get_input_text()

        if not title or not title.strip():
            self.view.show_error("Please enter a todo item")
            return

        try:
            self.model.add_item(title)
            self.view.clear_input()
            self.view.focus_input()
        except ValueError as e:
            self.view.show_error(str(e))
            logger.error(f"Failed to add item: {e}")

    def on_delete_item(self) -> None:
        """Handle delete item action."""
        if not self.view:
            return

        # Get selected index
        selection = self.view.listbox.curselection()
        if not selection:
            self.view.show_error("Please select an item to delete")
            return

        index = selection[0]
        if index not in self._item_id_map:
            self.view.show_error("Invalid selection")
            return

        # Get UUID from mapping
        from uuid import UUID

        item_id = UUID(self._item_id_map[index])

        # Remove item
        if self.model.remove_item(item_id):
            logger.info(f"Item deleted: {item_id}")
        else:
            self.view.show_error("Failed to delete item")

    def on_toggle_item(self) -> None:
        """Handle toggle item action."""
        if not self.view:
            return

        # Get selected index
        selection = self.view.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index not in self._item_id_map:
            return

        # Get UUID from mapping
        from uuid import UUID

        item_id = UUID(self._item_id_map[index])

        # Toggle item
        if self.model.toggle_item(item_id):
            logger.info(f"Item toggled: {item_id}")

    def on_clear_completed(self) -> None:
        """Handle clear completed action."""
        count = self.model.clear_completed()
        if count > 0 and self.view:
            self.view.show_info(f"Cleared {count} completed item(s)")

    def on_clear_all(self) -> None:
        """Handle clear all action."""
        if self.view:
            from tkinter import messagebox

            if messagebox.askyesno("Confirm", "Clear all items?"):
                self.model.clear_all()
                self.view.show_info("All items cleared")
