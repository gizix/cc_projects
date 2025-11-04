"""Thread-safe async worker for GUI operations."""

import queue
import threading
from typing import Any, Callable

import tkinter as tk
from loguru import logger


class AsyncWorker:
    """Thread-safe worker for running async operations in GUI."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize async worker.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.queue: queue.Queue[Callable[[], None]] = queue.Queue()
        self._check_queue()
        logger.debug("AsyncWorker initialized")

    def _check_queue(self) -> None:
        """Process queue in main thread."""
        try:
            while True:
                callback = self.queue.get_nowait()
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error in queue callback: {e}")
        except queue.Empty:
            pass
        finally:
            # Check queue again after 100ms
            self.root.after(100, self._check_queue)

    def run_async(
        self,
        task: Callable[[], Any],
        on_complete: Callable[[Any | None, Exception | None], None],
    ) -> threading.Thread:
        """Run task in thread, call on_complete in main thread.

        Args:
            task: Task function to run in background
            on_complete: Callback function called with (result, error)

        Returns:
            Thread object
        """

        def worker() -> None:
            """Worker thread function."""
            try:
                logger.debug(f"Starting async task: {task.__name__}")
                result = task()
                logger.debug(f"Task completed: {task.__name__}")
                self.queue.put(lambda: on_complete(result, None))
            except Exception as e:
                logger.error(f"Task failed: {task.__name__} - {e}")
                self.queue.put(lambda: on_complete(None, e))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread

    def run_async_with_progress(
        self,
        task: Callable[[Callable[[int], None]], Any],
        on_progress: Callable[[int], None],
        on_complete: Callable[[Any | None, Exception | None], None],
    ) -> threading.Thread:
        """Run task with progress updates.

        Args:
            task: Task function that accepts progress callback
            on_progress: Progress callback (percentage 0-100)
            on_complete: Completion callback (result, error)

        Returns:
            Thread object
        """

        def progress_callback(percentage: int) -> None:
            """Thread-safe progress callback.

            Args:
                percentage: Progress percentage (0-100)
            """
            self.queue.put(lambda: on_progress(percentage))

        def worker() -> None:
            """Worker thread function."""
            try:
                logger.debug(f"Starting async task with progress: {task.__name__}")
                result = task(progress_callback)
                logger.debug(f"Task completed: {task.__name__}")
                self.queue.put(lambda: on_complete(result, None))
            except Exception as e:
                logger.error(f"Task failed: {task.__name__} - {e}")
                self.queue.put(lambda: on_complete(None, e))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread


class ProgressDialog(tk.Toplevel):
    """Modal progress dialog for long-running operations."""

    def __init__(
        self,
        parent: tk.Tk,
        title: str = "Processing...",
        message: str = "Please wait...",
    ) -> None:
        """Initialize progress dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message
        """
        super().__init__(parent)
        self.title(title)
        self.result: Any = None
        self.error: Exception | None = None

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        import ttkbootstrap as ttk

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        self.message_label = ttk.Label(frame, text=message, font=("Segoe UI", 10))
        self.message_label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=300)
        self.progress.pack(pady=10)
        self.progress.start()

        # Center on parent
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

        # Prevent closing
        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def set_message(self, message: str) -> None:
        """Update progress message.

        Args:
            message: New message
        """
        self.message_label.config(text=message)

    def set_progress(self, percentage: int) -> None:
        """Set determinate progress.

        Args:
            percentage: Progress percentage (0-100)
        """
        self.progress.stop()
        self.progress.config(mode="determinate", value=percentage)

    def close_with_result(self, result: Any, error: Exception | None) -> None:
        """Close dialog with result.

        Args:
            result: Task result
            error: Task error (if any)
        """
        self.result = result
        self.error = error
        self.destroy()

    @staticmethod
    def run_with_dialog(
        parent: tk.Tk,
        task: Callable[[], Any],
        title: str = "Processing...",
        message: str = "Please wait...",
    ) -> tuple[Any | None, Exception | None]:
        """Run task with modal progress dialog.

        Args:
            parent: Parent window
            task: Task function to run
            title: Dialog title
            message: Dialog message

        Returns:
            Tuple of (result, error)
        """
        dialog = ProgressDialog(parent, title, message)

        def on_complete(result: Any, error: Exception | None) -> None:
            """Completion callback.

            Args:
                result: Task result
                error: Task error (if any)
            """
            dialog.close_with_result(result, error)

        worker = AsyncWorker(parent)
        worker.run_async(task, on_complete)

        # Wait for dialog to close
        parent.wait_window(dialog)

        return dialog.result, dialog.error
