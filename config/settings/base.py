"""Base Django settings shared by every environment.

Environment-specific modules (`development.py`, `production.py`) import
everything from here with `from .base import *` and only override what
actually differs between environments.
"""

from __future__ import annotations

from pathlib import Path

import dj_database_url

from config.settings.env import get_settings
from core.infrastructure.logging.setup import build_logging_config, configure_structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
ALLOWED_HOSTS = settings.allowed_hosts_list

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "apps.accounts",
    "apps.requests",
    "apps.bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    # No cookies/sessions exist to protect, and the one POST endpoint
    # (the Telegram webhook) is deliberately @csrf_exempt with its own
    # secret-token auth — but enabling this is free defense-in-depth
    # against any future state-changing view, and silences Django's
    # `check --deploy` W003 warning.
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    # No forced ssl_require here: whether a connection needs SSL depends on
    # the specific host (Render's does; Railway's internal Postgres
    # networking doesn't), not on ENVIRONMENT. If a given DATABASE_URL
    # needs SSL, add `?sslmode=require` to that URL directly — dj-database-url
    # already parses querystring params like that into OPTIONS automatically.
    "default": dj_database_url.parse(settings.DATABASE_URL, conn_max_age=60),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# --- Structured logging (structlog, routed through Django's LOGGING) ---
configure_structlog()
LOGGING = build_logging_config(log_level=settings.LOG_LEVEL, json_logs=not DEBUG)

# --- Application-specific settings (consumed by apps.bot / core.infrastructure) ---
BOT_TOKEN = settings.BOT_TOKEN
ADMIN_ID = settings.ADMIN_ID
WEBHOOK_SECRET = settings.WEBHOOK_SECRET
WEBHOOK_PATH = settings.WEBHOOK_PATH
PUBLIC_BASE_URL = settings.resolved_public_base_url
KEEPALIVE_ENABLED = settings.KEEPALIVE_ENABLED
KEEPALIVE_INTERVAL_SECONDS = settings.KEEPALIVE_INTERVAL_SECONDS
