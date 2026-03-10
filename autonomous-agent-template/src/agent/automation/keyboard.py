"""pyautogui keyboard helpers with headless guard."""

from __future__ import annotations

import os
import sys
import time


def is_headless() -> bool:
    if os.environ.get("AGENT_HEADLESS", "").lower() in ("1", "true"):
        return True
    if sys.platform == "linux" and not os.environ.get("DISPLAY"):
        return True
    return False


def type_text(text: str, interval: float = 0.05) -> None:
    if is_headless():
        raise RuntimeError("Cannot type text in headless environment")
    import pyautogui

    pyautogui.typewrite(text, interval=interval)


def press_keys(*keys: str) -> None:
    if is_headless():
        raise RuntimeError("Cannot press keys in headless environment")
    import pyautogui

    pyautogui.hotkey(*keys)


def press_key(key: str) -> None:
    if is_headless():
        raise RuntimeError("Cannot press key in headless environment")
    import pyautogui

    pyautogui.press(key)
