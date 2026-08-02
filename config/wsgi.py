"""WSGI entrypoint, kept for local tooling (e.g. `manage.py runserver`).

Production always runs the ASGI app (config.asgi:application) under an
uvicorn worker so the async bot/webhook code path is used.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
