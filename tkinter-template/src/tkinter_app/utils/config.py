"""Configuration management with JSON persistence."""

import json
from pathlib import Path
from typing import Any

from loguru import logger
from platformdirs import user_config_dir


class AppConfig:
    """Application configuration manager with JSON persistence."""

    def __init__(self, app_name: str = "TkinterApp") -> None:
        """Initialize configuration manager.

        Args:
            app_name: Application name for config directory
        """
        self.app_name = app_name
        self.config_dir = Path(user_config_dir(app_name))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.settings = self._load()
        logger.info(f"Config loaded from {self.config_file}")

    def _load(self) -> dict[str, Any]:
        """Load settings from file.

        Returns:
            Settings dictionary
        """
        if self.config_file.exists():
            try:
                content = self.config_file.read_text(encoding="utf-8")
                return json.loads(content)
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load config: {e}")
                return self._defaults()
        return self._defaults()

    def _defaults(self) -> dict[str, Any]:
        """Get default settings.

        Returns:
            Default settings dictionary
        """
        # Try to load from resources
        resources_path = Path(__file__).parent.parent / "resources" / "config"
        default_file = resources_path / "default_settings.json"

        if default_file.exists():
            try:
                content = default_file.read_text(encoding="utf-8")
                return json.loads(content)
            except (json.JSONDecodeError, OSError):
                pass

        # Fallback defaults
        return {
            "theme": "litera",
            "window_size": {"width": 800, "height": 600},
            "window_position": {"x": None, "y": None},
            "recent_files": [],
            "max_recent_files": 10,
            "auto_save": True,
            "auto_save_interval": 300,
            "font_family": "Segoe UI",
            "font_size": 10,
            "show_toolbar": True,
            "show_statusbar": True,
        }

    def save(self) -> None:
        """Save settings to file."""
        try:
            content = json.dumps(self.settings, indent=2)
            self.config_file.write_text(content, encoding="utf-8")
            logger.info("Config saved successfully")
        except OSError as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value.

        Args:
            key: Setting key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        keys = key.split(".")
        value = self.settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set setting value.

        Args:
            key: Setting key (supports dot notation for nested keys)
            value: Setting value
        """
        keys = key.split(".")

        if len(keys) == 1:
            self.settings[key] = value
        else:
            # Handle nested keys
            current = self.settings
            for k in keys[:-1]:
                if k not in current or not isinstance(current[k], dict):
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value

        self.save()

    def add_recent_file(self, filepath: str) -> None:
        """Add file to recent files list.

        Args:
            filepath: Path to file
        """
        recent = self.settings.get("recent_files", [])

        # Remove if already exists
        if filepath in recent:
            recent.remove(filepath)

        # Add to beginning
        recent.insert(0, filepath)

        # Limit size
        max_recent = self.settings.get("max_recent_files", 10)
        recent = recent[:max_recent]

        self.settings["recent_files"] = recent
        self.save()

    def clear_recent_files(self) -> None:
        """Clear recent files list."""
        self.settings["recent_files"] = []
        self.save()

    def reset(self) -> None:
        """Reset settings to defaults."""
        self.settings = self._defaults()
        self.save()
        logger.info("Config reset to defaults")
