"""Example data model for todo list application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from uuid import UUID, uuid4

from loguru import logger


@dataclass
class TodoItem:
    """A todo item."""

    title: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

    def toggle(self) -> None:
        """Toggle completion status."""
        self.completed = not self.completed
        logger.debug(f"Todo {self.id} toggled: completed={self.completed}")


class TodoModel:
    """Model for managing todo items."""

    def __init__(self) -> None:
        """Initialize todo model."""
        self.items: list[TodoItem] = []
        self._observers: list[Callable[[], None]] = []
        logger.debug("TodoModel initialized")

    def add_observer(self, callback: Callable[[], None]) -> None:
        """Add observer callback for model changes.

        Args:
            callback: Callback function to call on changes
        """
        self._observers.append(callback)
        logger.debug(f"Observer added: {callback.__name__}")

    def remove_observer(self, callback: Callable[[], None]) -> None:
        """Remove observer callback.

        Args:
            callback: Callback function to remove
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug(f"Observer removed: {callback.__name__}")

    def _notify_observers(self) -> None:
        """Notify all observers of changes."""
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in observer callback: {e}")

    def add_item(self, title: str) -> TodoItem:
        """Add new todo item.

        Args:
            title: Item title

        Returns:
            Created TodoItem
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        item = TodoItem(title=title.strip())
        self.items.append(item)
        logger.info(f"Todo item added: {item.title}")
        self._notify_observers()
        return item

    def remove_item(self, item_id: UUID) -> bool:
        """Remove todo item by ID.

        Args:
            item_id: Item UUID

        Returns:
            True if removed, False if not found
        """
        for item in self.items:
            if item.id == item_id:
                self.items.remove(item)
                logger.info(f"Todo item removed: {item.title}")
                self._notify_observers()
                return True
        return False

    def toggle_item(self, item_id: UUID) -> bool:
        """Toggle item completion status.

        Args:
            item_id: Item UUID

        Returns:
            True if toggled, False if not found
        """
        for item in self.items:
            if item.id == item_id:
                item.toggle()
                self._notify_observers()
                return True
        return False

    def get_item(self, item_id: UUID) -> TodoItem | None:
        """Get item by ID.

        Args:
            item_id: Item UUID

        Returns:
            TodoItem if found, None otherwise
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_all_items(self) -> list[TodoItem]:
        """Get all todo items.

        Returns:
            List of TodoItem objects
        """
        return self.items.copy()

    def get_active_items(self) -> list[TodoItem]:
        """Get active (not completed) items.

        Returns:
            List of active TodoItem objects
        """
        return [item for item in self.items if not item.completed]

    def get_completed_items(self) -> list[TodoItem]:
        """Get completed items.

        Returns:
            List of completed TodoItem objects
        """
        return [item for item in self.items if item.completed]

    def clear_completed(self) -> int:
        """Remove all completed items.

        Returns:
            Number of items removed
        """
        count = len([item for item in self.items if item.completed])
        self.items = [item for item in self.items if not item.completed]
        if count > 0:
            logger.info(f"Cleared {count} completed items")
            self._notify_observers()
        return count

    def clear_all(self) -> None:
        """Remove all items."""
        count = len(self.items)
        self.items.clear()
        if count > 0:
            logger.info(f"Cleared all {count} items")
            self._notify_observers()
