"""Repository interface for Customer persistence.

The application layer depends on this Protocol, not on Django — the
concrete implementation lives in `core.infrastructure.repositories`.
Async because every consumer (aiogram handlers/middlewares) is async.
"""

from __future__ import annotations

from typing import Protocol

from core.domain.entities.customer import Customer


class CustomerRepository(Protocol):
    async def get_by_telegram_id(self, telegram_id: int) -> Customer | None: ...

    async def upsert(
        self,
        *,
        telegram_id: int,
        first_name: str,
        last_name: str | None,
        username: str | None,
    ) -> Customer:
        """Create the customer on first contact, or refresh their Telegram profile."""
        ...

    async def update_phone_number(self, customer_id: int, phone_number: str) -> None: ...
