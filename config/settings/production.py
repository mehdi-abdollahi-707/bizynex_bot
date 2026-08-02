"""Render production overrides."""

from urllib.parse import urlparse

from config.settings.base import *  # noqa: F401,F403
from config.settings.base import ALLOWED_HOSTS, PUBLIC_BASE_URL

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Start conservative (1 day, no subdomains/preload) per Django's own
# warning that HSTS is hard to safely walk back once a browser has
# cached it — raise this once the deployment is confirmed stable.
SECURE_HSTS_SECONDS = 86400
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# The host platform (Render, Railway, ...) assigns the public hostname
# dynamically — add it automatically so a forgotten ALLOWED_HOSTS entry
# can't 400 the webhook.
if PUBLIC_BASE_URL:
    _public_host = urlparse(PUBLIC_BASE_URL).netloc
    if _public_host and _public_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_public_host)
