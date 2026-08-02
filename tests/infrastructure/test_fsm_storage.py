"""`_state_value()` normalizes whatever aiogram passes into a plain string.

The read/write round-trip through `TelegramFSMState` itself needs a live
Postgres connection (pytest-django spins up a real test database), so
those cases live in test_fsm_storage_db.py instead of here.
"""

from aiogram.fsm.state import State, StatesGroup

from core.infrastructure.telegram.fsm_storage import _state_value


class _ExampleFlow(StatesGroup):
    choosing_service = State()


def test_none_state_is_none() -> None:
    assert _state_value(None) is None


def test_state_object_uses_its_qualified_state_string() -> None:
    # A State only carries its final ".state" string once bound to a
    # StatesGroup (aiogram prefixes it with the group name) — this is how
    # real handlers reference states, e.g. `EstimatorFlow.choosing_service`.
    assert _state_value(_ExampleFlow.choosing_service) == _ExampleFlow.choosing_service.state
    assert _state_value(_ExampleFlow.choosing_service) == "_ExampleFlow:choosing_service"


def test_plain_string_state_passes_through() -> None:
    assert _state_value("SomeGroup:step") == "SomeGroup:step"
