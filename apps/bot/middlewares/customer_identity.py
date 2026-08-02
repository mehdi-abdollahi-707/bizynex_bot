"""Upserts the Customer record on every interaction and injects it into
every handler's kwargs, so no handler needs to repeat that lookup.

Registered as an outer middleware on both the message and callback_query
observers, so it's the one place recording "a real user acted" — this is
also where the LOGGING spec's "user actions" entries come from.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.infrastructure.repositories.django_customer_repository import (
    DjangoCustomerRepository,
)

logger = structlog.get_logger("bizynex")

_repository = DjangoCustomerRepository()


class CustomerIdentityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        telegram_user = data.get("event_from_user")

        if telegram_user is not None:
            customer = await _repository.upsert(
                telegram_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
            )
            data["customer"] = customer
            logger.info(
                "customer.interaction",
                telegram_id=telegram_user.id,
                customer_id=customer.id,
            )

        return await handler(event, data)
