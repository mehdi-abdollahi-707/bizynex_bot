"""Shared fixtures for handler-level integration tests.

Handlers are called directly — bypassing aiogram's own filter/dispatch
machinery, which is framework code we don't need to re-test — with a real
`FSMContext` backed by in-memory storage (not the production
`DjangoFSMStorage`, which needs Postgres). This exercises the real
conversation logic (question sequencing, validation, state transitions)
without a database; only repository calls are mocked at the boundary.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from core.domain.entities.customer import Customer


@pytest.fixture
def fake_customer() -> Customer:
    return Customer(id=1, telegram_id=1001, first_name="علی", last_name="محمدی", username="ali_m")


@pytest.fixture
def make_state():
    def _make(bot_id: int = 1, chat_id: int = 1001, user_id: int = 1001) -> FSMContext:
        storage = MemoryStorage()
        key = StorageKey(bot_id=bot_id, chat_id=chat_id, user_id=user_id)
        return FSMContext(storage=storage, key=key)

    return _make


@pytest.fixture
def make_callback():
    """A stand-in CallbackQuery: `.message.edit_text` and `.answer` are
    AsyncMocks so handler behavior can be asserted on; every other
    attribute is settable via keyword overrides.
    """

    def _make(**overrides):
        message = MagicMock()
        message.edit_text = AsyncMock()

        callback = MagicMock()
        callback.message = message
        callback.answer = AsyncMock()
        callback.from_user = MagicMock(id=1001)

        for key, value in overrides.items():
            setattr(callback, key, value)
        return callback

    return _make


@pytest.fixture
def make_message():
    """A stand-in Message: `.answer` is an AsyncMock; `.text`/`.document`/
    `.photo` and anything else default to sensible empty values, settable
    via keyword overrides.
    """

    def _make(text: str | None = None, **overrides):
        message = MagicMock()
        message.answer = AsyncMock()
        message.text = text
        message.document = overrides.pop("document", None)
        message.photo = overrides.pop("photo", None)

        for key, value in overrides.items():
            setattr(message, key, value)
        return message

    return _make
