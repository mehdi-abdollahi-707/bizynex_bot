"""Postgres-backed aiogram FSM storage — deliberately not Redis.

Render's free-tier web service has no persistent memory across restarts,
and every cold start after idle sleep is effectively a fresh process, so
conversation state (which menu step a customer is on, their in-progress
estimator/request-form answers) has to live in the database or it's lost
mid-conversation. This implements aiogram's `BaseStorage` on top of the
`TelegramFSMState` model instead.
"""

from __future__ import annotations

from typing import Any

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from apps.bot.models import TelegramFSMState


def _state_value(state: StateType) -> str | None:
    if state is None:
        return None
    if isinstance(state, State):
        return state.state
    return str(state)


class DjangoFSMStorage(BaseStorage):
    """Reads and writes FSM state/data through the Django async ORM."""

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        await TelegramFSMState.objects.aupdate_or_create(
            bot_id=key.bot_id,
            chat_id=key.chat_id,
            user_id=key.user_id,
            thread_id=key.thread_id or 0,
            destiny=key.destiny,
            defaults={"state": _state_value(state)},
        )

    async def get_state(self, key: StorageKey) -> str | None:
        record = await TelegramFSMState.objects.filter(
            bot_id=key.bot_id,
            chat_id=key.chat_id,
            user_id=key.user_id,
            thread_id=key.thread_id or 0,
            destiny=key.destiny,
        ).afirst()
        return record.state if record else None

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        await TelegramFSMState.objects.aupdate_or_create(
            bot_id=key.bot_id,
            chat_id=key.chat_id,
            user_id=key.user_id,
            thread_id=key.thread_id or 0,
            destiny=key.destiny,
            defaults={"data": dict(data)},
        )

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        record = await TelegramFSMState.objects.filter(
            bot_id=key.bot_id,
            chat_id=key.chat_id,
            user_id=key.user_id,
            thread_id=key.thread_id or 0,
            destiny=key.destiny,
        ).afirst()
        return dict(record.data) if record else {}

    async def close(self) -> None:
        """No persistent connection/pool of our own to close — Django owns it."""
