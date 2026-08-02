"""DB-backed tests for CustomerIdentityMiddleware — called directly with a
fake `handler`, so this needs a real Postgres connection (the upsert) but
not the full webhook/dispatcher machinery.
"""

import pytest
from aiogram.types import User

from apps.bot.middlewares.customer_identity import CustomerIdentityMiddleware
from core.infrastructure.repositories.django_customer_repository import (
    DjangoCustomerRepository,
)

pytestmark = pytest.mark.django_db(transaction=True)


async def test_upserts_the_customer_and_injects_it_into_handler_data() -> None:
    middleware = CustomerIdentityMiddleware()
    telegram_user = User(id=777, is_bot=False, first_name="علی", last_name="محمدی")
    data = {"event_from_user": telegram_user}

    seen_data = {}

    async def fake_handler(event, handler_data):
        seen_data.update(handler_data)
        return "handled"

    result = await middleware(fake_handler, event=object(), data=data)

    assert result == "handled"
    assert "customer" in seen_data
    assert seen_data["customer"].telegram_id == 777
    assert seen_data["customer"].first_name == "علی"

    persisted = await DjangoCustomerRepository().get_by_telegram_id(777)
    assert persisted is not None


async def test_repeat_interactions_reuse_the_same_customer_row() -> None:
    middleware = CustomerIdentityMiddleware()
    telegram_user = User(id=888, is_bot=False, first_name="رضا")

    async def fake_handler(event, handler_data):
        return handler_data["customer"]

    first = await middleware(fake_handler, event=object(), data={"event_from_user": telegram_user})
    second = await middleware(fake_handler, event=object(), data={"event_from_user": telegram_user})

    assert first.id == second.id


async def test_skips_upsert_when_no_telegram_user_in_context() -> None:
    middleware = CustomerIdentityMiddleware()

    async def fake_handler(event, handler_data):
        assert "customer" not in handler_data
        return "handled"

    result = await middleware(fake_handler, event=object(), data={})

    assert result == "handled"
