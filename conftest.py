"""Root pytest conftest.

Ensures every required environment variable has a safe dummy value before
pytest-django triggers `django.setup()`, so the test suite never depends on
a real `.env` file or a live secret being present in CI.
"""

import os

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/bizynex_test")
os.environ.setdefault("BOT_TOKEN", "123456:TEST-TOKEN")
os.environ.setdefault("ADMIN_ID", "123456789")
os.environ.setdefault("WEBHOOK_SECRET", "test-webhook-secret")
