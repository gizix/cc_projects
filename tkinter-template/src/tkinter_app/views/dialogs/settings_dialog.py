"""Settings dialog."""

import tkinter as tk
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from tkinter_app.utils import AppConfig


class SettingsDialog(tk.Toplevel):
    """Modal settings dialog."""

    def __init__(self, parent: tk.Tk, config: AppConfig) -> None:
        """Initialize settings dialog.

        Args:
            parent: Parent window
            config: Application configuration
        """
        super().__init__(parent)
        self.title("Settings")
        self.config = config
        self.result: dict[str, Any] | None = None

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

        # Theme selection
        ttk.Label(main_frame, text="Theme:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=W, pady=5
        )

        self.theme_var = tk.StringVar(value=self.config.get("theme", "litera"))
        theme_combo = ttk.Combobox(
            main_frame,
            textvariable=self.theme_var,
            values=[
                "cosmo",
                "flatly",
                "litera",
                "minty",
                "pulse",
                "sandstone",
                "united",
                "yeti",
                "morph",
                "journal",
                "darkly",
                "solar",
                "superhero",
                "vapor",
            ],
            state="readonly",
            width=20,
        )
        theme_combo.grid(row=0, column=1, sticky=W, pady=5, padx=(10, 0))

        # Auto-save
        self.auto_save_var = tk.BooleanVar(value=self.config.get("auto_save", True))
        auto_save_check = ttk.Checkbutton(
            main_frame,
            text="Enable auto-save",
            variable=self.auto_save_var,
            bootstyle="round-toggle",
        )
        auto_save_check.grid(row=1, column=0, columnspan=2, sticky=W, pady=10)

        # Font size
        ttk.Label(main_frame, text="Font size:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=W, pady=5
        )

        self.font_size_var = tk.IntVar(value=self.config.get("font_size", 10))
        font_size_spin = ttk.Spinbox(
            main_frame,
            from_=8,
            to=16,
            textvariable=self.font_size_var,
            width=10,
        )
        font_size_spin.grid(row=2, column=1, sticky=W, pady=5, padx=(10, 0))

        # Show toolbar
        self.show_toolbar_var = tk.BooleanVar(
            value=self.config.get("show_toolbar", True)
        )
        toolbar_check = ttk.Checkbutton(
            main_frame,
            text="Show toolbar",
            variable=self.show_toolbar_var,
            bootstyle="round-toggle",
        )
        toolbar_check.grid(row=3, column=0, columnspan=2, sticky=W, pady=5)

        # Show statusbar
        self.show_statusbar_var = tk.BooleanVar(
            value=self.config.get("show_statusbar", True)
        )
        statusbar_check = ttk.Checkbutton(
            main_frame,
            text="Show statusbar",
            variable=self.show_statusbar_var,
            bootstyle="round-toggle",
        )
        statusbar_check.grid(row=4, column=0, columnspan=2, sticky=W, pady=5)

        # Separator
        ttk.Separator(main_frame, orient=HORIZONTAL).grid(
            row=5, column=0, columnspan=2, sticky=EW, pady=15
        )

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, sticky=E)

        ttk.Button(
            button_frame,
            text="OK",
            command=self.on_ok,
            bootstyle=PRIMARY,
            width=10,
        ).pack(side=RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=10,
        ).pack(side=RIGHT)

    def _center_on_parent(self, parent: tk.Tk) -> None:
        """Center dialog on parent window.

        Args:
            parent: Parent window
        """
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
        self.result = {
            "theme": self.theme_var.get(),
            "auto_save": self.auto_save_var.get(),
            "font_size": self.font_size_var.get(),
            "show_toolbar": self.show_toolbar_var.get(),
            "show_statusbar": self.show_statusbar_var.get(),
        }
        self.destroy()

    def on_cancel(self) -> None:
        """Handle Cancel button."""
        self.result = None
        self.destroy()

    @staticmethod
    def show_dialog(parent: tk.Tk, config: AppConfig) -> dict[str, Any] | None:
        """Show settings dialog and return result.

        Args:
            parent: Parent window
            config: Application configuration

        Returns:
            Settings dict if OK pressed, None if cancelled
        """
        dialog = SettingsDialog(parent, config)
        parent.wait_window(dialog)
        return dialog.result
