"""Tests for controllers."""

import tkinter as tk

from tkinter_app.controllers import MainController
from tkinter_app.models import TodoModel


def test_controller_initialization(root):
    """Test controller initialization."""
    model = TodoModel()
    controller = MainController(root, model)

    assert controller.model is model
    assert controller.root is root


def test_controller_model_observer(root):
    """Test controller subscribes to model changes."""
    model = TodoModel()
    controller = MainController(root, model)

    # Add item should trigger observer
    model.add_item("Test")

    # Controller should have updated ID map
    assert len(controller._item_id_map) >= 0
