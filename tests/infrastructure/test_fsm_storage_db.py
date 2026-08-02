"""DB-backed round-trip tests for DjangoFSMStorage.

Requires a live PostgreSQL connection (pytest-django creates a real test
database via `DATABASE_URL`) — these will fail in an environment with no
reachable Postgres, which is expected and not a code defect.
"""

import pytest
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey

from core.infrastructure.telegram.fsm_storage import DjangoFSMStorage

pytestmark = pytest.mark.django_db(transaction=True)


def _key(**overrides) -> StorageKey:
    defaults = {"bot_id": 1, "chat_id": 100, "user_id": 100}
    return StorageKey(**{**defaults, **overrides})


async def test_set_and_get_state_round_trip() -> None:
    storage = DjangoFSMStorage()
    key = _key()

    await storage.set_state(key, State(state="EstimatorFlow:choosing_service"))

    assert await storage.get_state(key) == "EstimatorFlow:choosing_service"


async def test_get_state_defaults_to_none() -> None:
    storage = DjangoFSMStorage()
    assert await storage.get_state(_key(chat_id=999)) is None


async def test_set_and_get_data_round_trip() -> None:
    storage = DjangoFSMStorage()
    key = _key()

    await storage.set_data(key, {"answers": {"website_type": "شرکتی"}})

    assert await storage.get_data(key) == {"answers": {"website_type": "شرکتی"}}


async def test_get_data_defaults_to_empty_dict() -> None:
    storage = DjangoFSMStorage()
    assert await storage.get_data(_key(chat_id=998)) == {}


async def test_different_users_do_not_share_state() -> None:
    storage = DjangoFSMStorage()
    key_a = _key(user_id=1)
    key_b = _key(user_id=2)

    await storage.set_state(key_a, State(state="A"))
    await storage.set_state(key_b, State(state="B"))

    assert await storage.get_state(key_a) == "A"
    assert await storage.get_state(key_b) == "B"
