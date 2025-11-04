"""Main application class."""

import sys
import tkinter as tk
from pathlib import Path

import ttkbootstrap as ttk
from dotenv import load_dotenv
from loguru import logger

from tkinter_app.controllers.main_controller import MainController
from tkinter_app.models import TodoModel
from tkinter_app.utils import AppConfig
from tkinter_app.views.dialogs.settings_dialog import SettingsDialog
from tkinter_app.views.main_view import MainView


class TkinterApp(ttk.Window):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize application."""
        # Load environment variables
        load_dotenv()

        # Initialize config
        self.config = AppConfig("TkinterApp")

        # Initialize window with theme
        theme = self.config.get("theme", "litera")
        super().__init__(themename=theme)

        # Setup logging
        self._setup_logging()

        # Initialize MVC components
        self.model = TodoModel()
        self.controller = MainController(self, self.model)

        # Setup window
        self._setup_window()

        # Create menu
        self._create_menu()

        # Create main view
        self.main_view = MainView(self, self.controller)
        self.main_view.pack(fill="both", expand=True)

        # Connect controller and view
        self.controller.set_view(self.main_view)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        logger.info("Application initialized")

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Remove default handler
        logger.remove()

        # Add console handler
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO",
        )

        # Add file handler
        log_file = Path.home() / ".tkinter_app" / "app.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            rotation="10 MB",
            retention="7 days",
            level="DEBUG",
        )

    def _setup_window(self) -> None:
        """Setup window properties."""
        self.title("Todo App - Tkinter Template")

        # Get saved window size
        width = self.config.get("window_size.width", 800)
        height = self.config.get("window_size.height", 600)
        self.geometry(f"{width}x{height}")

        # Get saved window position
        pos_x = self.config.get("window_position.x")
        pos_y = self.config.get("window_position.y")
        if pos_x is not None and pos_y is not None:
            self.geometry(f"+{pos_x}+{pos_y}")
        else:
            # Center window
            self.position_center()

        # Set minimum size
        self.minsize(600, 400)

        # Set icon (if exists)
        icon_path = self._get_resource_path("resources/images/icon.png")
        if icon_path.exists():
            try:
                self.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")

    def _get_resource_path(self, relative_path: str) -> Path:
        """Get absolute path to resource.

        Args:
            relative_path: Relative path from package root

        Returns:
            Absolute path to resource
        """
        if getattr(sys, "frozen", False):
            # Running in PyInstaller bundle
            base_path = Path(sys._MEIPASS)  # type: ignore
        else:
            # Running in normal Python environment
            base_path = Path(__file__).parent

        return base_path / relative_path

    def _create_menu(self) -> None:
        """Create application menu."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="New", command=self.on_new, accelerator="Ctrl+N"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Settings...", command=self.on_settings, accelerator="Ctrl+,"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit", command=self.on_closing, accelerator="Ctrl+Q"
        )

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(
            label="Clear Completed", command=self.controller.on_clear_completed
        )
        edit_menu.add_command(
            label="Clear All", command=self.controller.on_clear_all
        )

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.on_about)

        # Bind keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.on_new())
        self.bind("<Control-comma>", lambda e: self.on_settings())
        self.bind("<Control-q>", lambda e: self.on_closing())

    def on_new(self) -> None:
        """Handle new action."""
        if self.main_view:
            self.main_view.focus_input()

    def on_settings(self) -> None:
        """Handle settings action."""
        result = SettingsDialog.show_dialog(self, self.config)

        if result:
            # Apply settings
            for key, value in result.items():
                self.config.set(key, value)

            # Apply theme (requires restart)
            if result["theme"] != self.style.theme_use():
                from tkinter import messagebox

                messagebox.showinfo(
                    "Theme Changed",
                    "Theme will be applied on next restart.",
                )

            logger.info("Settings updated")

    def on_about(self) -> None:
        """Handle about action."""
        from tkinter import messagebox

        messagebox.showinfo(
            "About",
            "Tkinter Todo App\n\n"
            "A modern Tkinter application template\n"
            "with MVC architecture.\n\n"
            "Version 0.1.0",
        )

    def on_closing(self) -> None:
        """Handle window closing."""
        # Save window position and size
        self.config.set("window_size.width", self.winfo_width())
        self.config.set("window_size.height", self.winfo_height())
        self.config.set("window_position.x", self.winfo_x())
        self.config.set("window_position.y", self.winfo_y())

        logger.info("Application closing")
        self.destroy()


def main() -> None:
    """Application entry point."""
    app = TkinterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
