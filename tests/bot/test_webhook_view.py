"""Webhook view tests.

Most of these reject before ever reaching the dispatcher, so they need no
database. The one full-dispatch test at the bottom does need a live
Postgres connection (the identity middleware's Customer upsert) — see its
own docstring.
"""

import json
from unittest.mock import AsyncMock

import pytest
from django.conf import settings
from django.test import AsyncClient
from django.urls import reverse


async def test_rejects_missing_secret_token() -> None:
    client = AsyncClient()
    response = await client.post(
        reverse("telegram-webhook"), data=b"{}", content_type="application/json"
    )
    assert response.status_code == 403


async def test_rejects_wrong_secret_token() -> None:
    client = AsyncClient()
    response = await client.post(
        reverse("telegram-webhook"),
        data=b"{}",
        content_type="application/json",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert response.status_code == 403


async def test_rejects_invalid_json() -> None:
    client = AsyncClient()
    response = await client.post(
        reverse("telegram-webhook"),
        data=b"not json at all {{{",
        content_type="application/json",
        headers={"X-Telegram-Bot-Api-Secret-Token": settings.WEBHOOK_SECRET},
    )
    assert response.status_code == 400


async def test_rejects_valid_json_with_invalid_update_schema() -> None:
    client = AsyncClient()
    response = await client.post(
        reverse("telegram-webhook"),
        data=b'{"totally": "not a telegram update"}',
        content_type="application/json",
        headers={"X-Telegram-Bot-Api-Secret-Token": settings.WEBHOOK_SECRET},
    )
    assert response.status_code == 400


async def test_rejects_get_requests() -> None:
    client = AsyncClient()
    response = await client.get(reverse("telegram-webhook"))
    assert response.status_code == 405


async def test_health_check_returns_ok() -> None:
    client = AsyncClient()
    response = await client.get(reverse("health-check"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db(transaction=True)
async def test_valid_start_command_dispatches_end_to_end(monkeypatch) -> None:
    """The one genuinely full-stack test: webhook view -> dispatcher ->
    CustomerIdentityMiddleware (real DB upsert) -> start handler -> a
    reply sent through the bot. The `Bot` itself is mocked so no real
    Telegram API call happens; everything else is production code.
    """
    fake_bot = AsyncMock()
    monkeypatch.setattr("apps.bot.views.get_bot", lambda: fake_bot)

    payload = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "date": 0,
            "chat": {"id": 5001, "type": "private"},
            "from": {"id": 5001, "is_bot": False, "first_name": "علی"},
            "text": "/start",
        },
    }

    client = AsyncClient()
    response = await client.post(
        reverse("telegram-webhook"),
        data=json.dumps(payload).encode(),
        content_type="application/json",
        headers={"X-Telegram-Bot-Api-Secret-Token": settings.WEBHOOK_SECRET},
    )

    assert response.status_code == 200
    fake_bot.send_message.assert_awaited_once()

    from core.infrastructure.repositories.django_customer_repository import (
        DjangoCustomerRepository,
    )

    customer = await DjangoCustomerRepository().get_by_telegram_id(5001)
    assert customer is not None
    assert customer.first_name == "علی"
