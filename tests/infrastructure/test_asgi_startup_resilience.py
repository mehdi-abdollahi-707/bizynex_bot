"""`_on_startup()` must never let a failing side effect (webhook
registration, keep-alive task creation) prevent the ASGI server from
finishing startup.

This is exactly the bug behind a real incident: a failed `set_webhook`
call (bad token, a transient Telegram API hiccup, or a host with
restricted outbound access) used to make the *entire* lifespan.startup
fail, so the ASGI server never started listening — which then surfaced
as a platform health-check failure, since nothing was there to answer
`/health/`. A health check should only reflect "is the web server up,"
not "did every startup side effect succeed."
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import config.asgi as asgi_module
import core.infrastructure.telegram.bot_factory as bot_factory_module
import core.infrastructure.telegram.keepalive as keepalive_module


@pytest.fixture(autouse=True)
def _reset_keepalive_task():
    asgi_module._keepalive_task = None
    yield
    if asgi_module._keepalive_task is not None:
        asgi_module._keepalive_task.cancel()
    asgi_module._keepalive_task = None


async def test_startup_does_not_raise_when_webhook_registration_fails(monkeypatch, settings):
    settings.PUBLIC_BASE_URL = "https://example.up.railway.app"
    settings.KEEPALIVE_ENABLED = False

    fake_bot = AsyncMock()
    fake_bot.set_webhook.side_effect = RuntimeError("Telegram API unreachable")
    monkeypatch.setattr(bot_factory_module, "get_bot", lambda: fake_bot)

    await asgi_module._on_startup()  # must not raise

    fake_bot.set_webhook.assert_awaited_once()


async def test_keepalive_still_starts_when_webhook_registration_fails(monkeypatch, settings):
    settings.PUBLIC_BASE_URL = "https://example.up.railway.app"
    settings.KEEPALIVE_ENABLED = True
    settings.KEEPALIVE_INTERVAL_SECONDS = 780

    fake_bot = AsyncMock()
    fake_bot.set_webhook.side_effect = RuntimeError("Telegram API unreachable")
    monkeypatch.setattr(bot_factory_module, "get_bot", lambda: fake_bot)

    keepalive_started = AsyncMock()
    monkeypatch.setattr(keepalive_module, "run_keepalive_loop", keepalive_started)

    await asgi_module._on_startup()

    assert asgi_module._keepalive_task is not None
    keepalive_started.assert_called_once()


async def test_startup_does_not_raise_when_keepalive_task_creation_fails(monkeypatch, settings):
    settings.PUBLIC_BASE_URL = "https://example.up.railway.app"
    settings.KEEPALIVE_ENABLED = True

    fake_bot = AsyncMock()
    monkeypatch.setattr(bot_factory_module, "get_bot", lambda: fake_bot)

    def _broken_keepalive(*args, **kwargs):
        raise RuntimeError("cannot build coroutine")

    monkeypatch.setattr(keepalive_module, "run_keepalive_loop", _broken_keepalive)

    await asgi_module._on_startup()  # must not raise

    fake_bot.set_webhook.assert_awaited_once()


async def test_startup_skips_everything_cleanly_when_no_public_url(settings):
    settings.PUBLIC_BASE_URL = None

    await asgi_module._on_startup()  # must not raise

    assert asgi_module._keepalive_task is None
