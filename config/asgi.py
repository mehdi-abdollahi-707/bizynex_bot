"""ASGI entrypoint. Gunicorn serves this via the uvicorn worker class.

Django's `ASGIHandler` doesn't implement the ASGI `lifespan` protocol —
Uvicorn detects that and simply skips calling startup/shutdown hooks, no
error. `LifespanMiddleware` below adds that support: on `lifespan.startup`
it registers the Telegram webhook and starts the keep-alive task; on
`lifespan.shutdown` it stops them cleanly. Everything else (`http` scope)
passes straight through to Django unchanged.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

import structlog
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

logger = structlog.get_logger("bizynex")

_keepalive_task: asyncio.Task | None = None


async def _on_startup() -> None:
    global _keepalive_task

    from django.conf import settings

    from core.infrastructure.telegram.bot_factory import get_bot
    from core.infrastructure.telegram.keepalive import run_keepalive_loop

    if not settings.RENDER_EXTERNAL_URL:
        logger.info("startup.webhook_registration_skipped", reason="no RENDER_EXTERNAL_URL")
        return

    base_url = settings.RENDER_EXTERNAL_URL.rstrip("/")

    bot = get_bot()
    webhook_url = f"{base_url}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.WEBHOOK_SECRET,
        drop_pending_updates=False,
    )
    logger.info("startup.webhook_registered", url=webhook_url)

    if settings.KEEPALIVE_ENABLED:
        health_url = f"{base_url}/health/"
        _keepalive_task = asyncio.create_task(
            run_keepalive_loop(
                url=health_url,
                interval_seconds=settings.KEEPALIVE_INTERVAL_SECONDS,
            )
        )
        logger.info(
            "startup.keepalive_started",
            url=health_url,
            interval_seconds=settings.KEEPALIVE_INTERVAL_SECONDS,
        )


async def _on_shutdown() -> None:
    from core.infrastructure.telegram.bot_factory import get_bot

    if _keepalive_task is not None:
        _keepalive_task.cancel()

    bot = get_bot()
    await bot.session.close()
    logger.info("shutdown.complete")


class LifespanMiddleware:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "lifespan":
            await self.app(scope, receive, send)
            return

        while True:
            message = await receive()

            if message["type"] == "lifespan.startup":
                try:
                    await _on_startup()
                except Exception as exc:
                    logger.exception("startup.failed")
                    await send({"type": "lifespan.startup.failed", "message": str(exc)})
                    return
                await send({"type": "lifespan.startup.complete"})

            elif message["type"] == "lifespan.shutdown":
                try:
                    await _on_shutdown()
                except Exception as exc:
                    logger.exception("shutdown.failed")
                    await send({"type": "lifespan.shutdown.failed", "message": str(exc)})
                    return
                await send({"type": "lifespan.shutdown.complete"})
                return


application = LifespanMiddleware(django_asgi_app)
