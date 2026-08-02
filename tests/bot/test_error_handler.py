"""The global error handler must log the real exception but only ever
show the customer a generic, friendly message — never exception details.
"""

from unittest.mock import AsyncMock

from aiogram.types import Chat, ErrorEvent, Message, Update, User

from apps.bot.handlers.error_handler import _resolve_chat_id, handle_unexpected_error

_USER = User(id=1, is_bot=False, first_name="Test")
_CHAT = Chat(id=42, type="private")


def _message_update() -> Update:
    message = Message(message_id=1, date=0, chat=_CHAT, from_user=_USER, text="hi")
    return Update(update_id=1, message=message)


async def test_sends_a_friendly_message_not_the_exception_text() -> None:
    bot = AsyncMock()
    event = ErrorEvent(
        update=_message_update(), exception=ValueError("super secret internal detail")
    )

    await handle_unexpected_error(event, bot)

    bot.send_message.assert_awaited_once()
    _, kwargs = bot.send_message.call_args
    assert kwargs["chat_id"] == 42
    assert "super secret internal detail" not in kwargs["text"]
    assert "مشکلی پیش آمد" in kwargs["text"]


async def test_returns_true_to_mark_the_error_as_handled() -> None:
    bot = AsyncMock()
    event = ErrorEvent(update=_message_update(), exception=RuntimeError("x"))

    result = await handle_unexpected_error(event, bot)

    assert result is True


async def test_does_not_raise_if_sending_the_notification_itself_fails() -> None:
    bot = AsyncMock()
    bot.send_message.side_effect = RuntimeError("telegram is down")
    event = ErrorEvent(update=_message_update(), exception=ValueError("original bug"))

    await handle_unexpected_error(event, bot)  # must not raise


def test_resolve_chat_id_from_message_update() -> None:
    event = ErrorEvent(update=_message_update(), exception=ValueError("x"))
    assert _resolve_chat_id(event) == 42


def test_resolve_chat_id_returns_none_when_no_chat_context() -> None:
    event = ErrorEvent(update=Update(update_id=1), exception=ValueError("x"))
    assert _resolve_chat_id(event) is None
