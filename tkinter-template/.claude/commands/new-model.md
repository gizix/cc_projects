---
description: Generate a new data model with observer pattern
argument-hint: <model-name>
model: sonnet
---

Create a new data model following the MVC observer pattern used in this template.

Arguments:
- $1: Model name in PascalCase (e.g., `UserProfile`, `AppSettings`)

The model should:

1. **File Location**: Create `src/tkinter_app/models/<snake_case_name>_model.py`

2. **Class Structure**:
```python
"""<Description> data model."""

from typing import Callable
from loguru import logger


class <ModelName>Model:
    """Model for managing <description>."""

    def __init__(self) -> None:
        """Initialize model."""
        self._data: dict = {}
        self._observers: list[Callable[[], None]] = []
        logger.debug(f"{self.__class__.__name__} initialized")

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

    # Add model-specific methods here
    # Remember to call self._notify_observers() after state changes
```

3. **Model Features**:
   - Observer pattern for notifying views of changes
   - Logging with loguru
   - Type hints on all methods
   - Docstrings for all public methods
   - Call `_notify_observers()` after any state change
   - Use dataclasses for data entities if appropriate

4. **Data Entities**: If model manages collections, consider creating a dataclass:
```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class <EntityName>:
    """A <description> entity."""

    name: str
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)
```

5. **Update __init__.py**: Add model to `src/tkinter_app/models/__init__.py`

6. **Integration**: Suggest how to integrate with controller and view

Generate the complete model with $1 as the name.
