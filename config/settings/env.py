"""Environment configuration loaded and validated with pydantic-settings.

Django's settings modules read from `get_settings()` instead of touching
`os.environ` directly, so every required variable is validated once, at
startup, with a clear error instead of failing deep inside request handling.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ENVIRONMENT: Literal["development", "production"] = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    DATABASE_URL: str

    BOT_TOKEN: str
    ADMIN_ID: int
    WEBHOOK_SECRET: str
    WEBHOOK_PATH: str = "/webhook/"
    RENDER_EXTERNAL_URL: str | None = None

    KEEPALIVE_ENABLED: bool = True
    KEEPALIVE_INTERVAL_SECONDS: int = 780

    LOG_LEVEL: str = "INFO"

    @field_validator("LOG_LEVEL")
    @classmethod
    def _uppercase_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached, validated Settings instance."""
    return Settings()  # type: ignore[call-arg]
