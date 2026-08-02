"""Selects the active Django settings module based on the ENVIRONMENT variable."""

import os

_environment = os.getenv("ENVIRONMENT", "development")

if _environment == "production":
    from config.settings.production import *  # noqa: F401,F403
else:
    from config.settings.development import *  # noqa: F401,F403
