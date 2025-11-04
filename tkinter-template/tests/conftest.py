"""Pytest configuration and fixtures."""

import tkinter as tk

import pytest


@pytest.fixture
def root():
    """Create root window for testing.

    Yields:
        Tkinter root window
    """
    root_window = tk.Tk()
    yield root_window
    root_window.destroy()


@pytest.fixture
def tk_var():
    """Create Tkinter StringVar for testing.

    Returns:
        Tkinter StringVar
    """
    return tk.StringVar()
