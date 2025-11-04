"""Tests for GUI components."""

from tkinter_app.controllers import MainController
from tkinter_app.models import TodoModel
from tkinter_app.views import MainView


def test_main_view_creation(root):
    """Test main view initializes correctly."""
    model = TodoModel()
    controller = MainController(root, model)
    view = MainView(root, controller)

    assert view.winfo_exists()
    assert view.controller is controller


def test_main_view_input(root):
    """Test input entry."""
    model = TodoModel()
    controller = MainController(root, model)
    view = MainView(root, controller)

    view.input_var.set("Test todo")
    assert view.get_input_text() == "Test todo"

    view.clear_input()
    assert view.get_input_text() == ""


def test_main_view_list_update(root):
    """Test listbox updates with items."""
    model = TodoModel()
    controller = MainController(root, model)
    view = MainView(root, controller)

    # Add items to model
    item1 = model.add_item("Todo 1")
    item2 = model.add_item("Todo 2")

    # Update view
    view.update_list(model.get_all_items())

    # Check listbox
    assert view.listbox.size() == 2
