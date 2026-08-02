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
    ALLOWED_HOSTS: str = "healthcheck.railway.app"

    DATABASE_URL: str

    BOT_TOKEN: str
    ADMIN_ID: int
    WEBHOOK_SECRET: str
    WEBHOOK_PATH: str = "/webhook/"

    # The app's own public URL, needed to register the Telegram webhook and
    # to self-ping for the keep-alive task. Never set more than one of
    # these by hand — PUBLIC_BASE_URL is the explicit, platform-agnostic
    # override; the other two are auto-injected by their respective
    # platforms and read automatically if PUBLIC_BASE_URL isn't set.
    PUBLIC_BASE_URL: str | None = None
    RENDER_EXTERNAL_URL: str | None = None  # Render: full URL, auto-injected
    RAILWAY_PUBLIC_DOMAIN: str | None = None  # Railway: bare domain, auto-injected

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

    @property
    def resolved_public_base_url(self) -> str | None:
        """The app's public URL, in priority order: explicit override,
        Render's (already a full URL), Railway's (a bare domain, needs a
        scheme prepended). None if not deployed behind any of these yet.
        """
        if self.PUBLIC_BASE_URL:
            return self.PUBLIC_BASE_URL.rstrip("/")
        if self.RENDER_EXTERNAL_URL:
            return self.RENDER_EXTERNAL_URL.rstrip("/")
        if self.RAILWAY_PUBLIC_DOMAIN:
            return f"https://{self.RAILWAY_PUBLIC_DOMAIN.rstrip('/')}"
        return None


@lru_cache
def get_settings() -> Settings:
    """Return a cached, validated Settings instance."""
    return Settings()  # type: ignore[call-arg]
