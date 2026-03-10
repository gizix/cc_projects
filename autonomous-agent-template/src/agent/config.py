"""Application configuration via Pydantic-Settings + .env file."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    data_dir: Path = Field(default=Path("data"), description="Directory for SQLite + credential store")
    worker_threads: int = Field(default=4, description="APScheduler thread pool size")
    log_level: str = Field(default="INFO")

    # --- Daemon ---
    pid_file: Path = Field(default=Path("data/agent.pid"))
    foreground: bool = Field(default=False, description="Run in foreground (no PID file)")

    # --- Web UI ---
    web_host: str = Field(default="127.0.0.1")
    web_port: int = Field(default=7890)
    web_open_browser: bool = Field(default=False)

    # --- Credentials ---
    master_password: str | None = Field(default=None, description="Encryption master password")
    credential_file: Path = Field(default=Path("data/.credentials.enc"))

    # --- LLM: Azure OpenAI (primary) ---
    azure_openai_api_key: str | None = Field(default=None)
    azure_openai_endpoint: str | None = Field(default=None)
    azure_openai_deployment: str | None = Field(default=None)
    azure_openai_api_version: str = Field(default="2024-02-15-preview")

    # --- LLM: OpenAI-compatible fallback ---
    openai_api_key: str | None = Field(default=None)
    openai_base_url: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o")

    # --- External DB (optional) ---
    external_db_url: str | None = Field(default=None, description="Any SQLAlchemy-compatible DB URL")

    def ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def internal_db_url(self) -> str:
        return f"sqlite:///{self.data_dir}/agent_ops.db"

    @property
    def scheduler_db_url(self) -> str:
        return f"sqlite:///{self.data_dir}/scheduler_jobs.db"


# Singleton — import this everywhere
settings = Settings()
