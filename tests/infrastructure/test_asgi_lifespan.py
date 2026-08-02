"""LifespanMiddleware must speak the ASGI lifespan protocol correctly,
independent of what the startup/shutdown hooks actually do.

`_on_startup`/`_on_shutdown` are monkeypatched to no-ops here so this test
needs neither a live Telegram token nor a database connection — it only
verifies the protocol handshake (startup.complete, shutdown.complete) and
that non-lifespan scopes are passed straight through to the wrapped app.
"""

import pytest

import config.asgi as asgi_module
from config.asgi import LifespanMiddleware


class _FakeApp:
    def __init__(self) -> None:
        self.called_with: dict | None = None

    async def __call__(self, scope, receive, send) -> None:
        self.called_with = scope


@pytest.fixture(autouse=True)
def _stub_hooks(monkeypatch):
    async def _noop() -> None:
        return None

    monkeypatch.setattr(asgi_module, "_on_startup", _noop)
    monkeypatch.setattr(asgi_module, "_on_shutdown", _noop)


async def test_non_lifespan_scope_passes_through() -> None:
    inner = _FakeApp()
    middleware = LifespanMiddleware(inner)

    await middleware({"type": "http"}, None, None)

    assert inner.called_with == {"type": "http"}


async def test_startup_sends_complete_message() -> None:
    middleware = LifespanMiddleware(_FakeApp())
    messages = iter([{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}])
    sent = []

    async def receive():
        return next(messages)

    async def send(message):
        sent.append(message)

    await middleware({"type": "lifespan"}, receive, send)

    assert {"type": "lifespan.startup.complete"} in sent
    assert {"type": "lifespan.shutdown.complete"} in sent
