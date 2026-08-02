"""`get_bot()`/`get_dispatcher()` must be process-wide singletons.

Neither call touches the network — aiogram's `Bot` only opens its HTTP
session lazily on first API call — so this needs no DB and no live token.
"""

from aiogram import Bot, Dispatcher

from core.infrastructure.telegram.bot_factory import get_bot, get_dispatcher
from core.infrastructure.telegram.fsm_storage import DjangoFSMStorage


def test_get_bot_returns_the_same_instance() -> None:
    assert get_bot() is get_bot()


def test_get_bot_returns_a_bot_instance() -> None:
    assert isinstance(get_bot(), Bot)


def test_get_dispatcher_returns_the_same_instance() -> None:
    assert get_dispatcher() is get_dispatcher()


def test_dispatcher_uses_django_fsm_storage() -> None:
    dispatcher = get_dispatcher()
    assert isinstance(dispatcher, Dispatcher)
    assert isinstance(dispatcher.storage, DjangoFSMStorage)
