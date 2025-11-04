"""Tests for data models."""

import pytest

from tkinter_app.models import TodoItem, TodoModel


def test_todo_item_creation():
    """Test creating a todo item."""
    item = TodoItem(title="Test todo")
    assert item.title == "Test todo"
    assert item.completed is False
    assert item.id is not None


def test_todo_item_toggle():
    """Test toggling todo item."""
    item = TodoItem(title="Test")
    assert item.completed is False

    item.toggle()
    assert item.completed is True

    item.toggle()
    assert item.completed is False


def test_todo_model_add_item():
    """Test adding item to model."""
    model = TodoModel()
    item = model.add_item("Test todo")

    assert len(model.items) == 1
    assert item.title == "Test todo"


def test_todo_model_add_empty_item():
    """Test adding empty item raises error."""
    model = TodoModel()

    with pytest.raises(ValueError):
        model.add_item("")


def test_todo_model_remove_item():
    """Test removing item from model."""
    model = TodoModel()
    item = model.add_item("Test")

    result = model.remove_item(item.id)
    assert result is True
    assert len(model.items) == 0


def test_todo_model_toggle_item():
    """Test toggling item in model."""
    model = TodoModel()
    item = model.add_item("Test")

    result = model.toggle_item(item.id)
    assert result is True
    assert item.completed is True


def test_todo_model_get_active_items():
    """Test getting active items."""
    model = TodoModel()
    item1 = model.add_item("Active")
    item2 = model.add_item("Completed")
    model.toggle_item(item2.id)

    active = model.get_active_items()
    assert len(active) == 1
    assert active[0].id == item1.id


def test_todo_model_clear_completed():
    """Test clearing completed items."""
    model = TodoModel()
    model.add_item("Active")
    item2 = model.add_item("Completed")
    model.toggle_item(item2.id)

    count = model.clear_completed()
    assert count == 1
    assert len(model.items) == 1


def test_todo_model_observer():
    """Test model observer pattern."""
    model = TodoModel()
    called = []

    def observer():
        called.append(True)

    model.add_observer(observer)
    model.add_item("Test")

    assert len(called) == 1
