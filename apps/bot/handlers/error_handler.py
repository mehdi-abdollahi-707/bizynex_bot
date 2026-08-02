"""Last-resort handler for any exception a handler doesn't catch itself.

Without this, a bug in a handler is invisible to the customer: the
webhook view's own try/except (Phase 3) stops it from crashing the HTTP
response, but the customer just sees their button tap do nothing — no
error, no way forward. This turns that silence into a friendly message
and an obvious way back to the main menu, and logs full context for
debugging. It never surfaces exception details to the customer, per the
spec's "never expose internal errors to users".
"""

from __future__ import annotations

import structlog
from aiogram import Bot, Router
from aiogram.types import ErrorEvent

from apps.bot.keyboards.navigation import build_page_keyboard

logger = structlog.get_logger("bizynex")

router = Router(name="error_handler")

_FRIENDLY_ERROR_TEXT = (
    "⚠️ متأسفانه مشکلی پیش آمد.\n\nلطفاً دوباره تلاش کنید یا به منوی اصلی بازگردید."
)


def _resolve_chat_id(event: ErrorEvent) -> int | None:
    update = event.update
    if update.message is not None:
        return update.message.chat.id
    if update.callback_query is not None and update.callback_query.message is not None:
        return update.callback_query.message.chat.id
    return None


@router.errors()
async def handle_unexpected_error(event: ErrorEvent, bot: Bot) -> bool:
    logger.exception(
        "handler.unhandled_exception",
        update_id=event.update.update_id,
        error=str(event.exception),
    )

    chat_id = _resolve_chat_id(event)
    if chat_id is not None:
        try:
            # "🔙 بازگشت" and "🏠 خانه" both point home here — there's no
            # single well-defined "previous page" to return to from an
            # arbitrary crash, so both buttons offer the same safe reset.
            await bot.send_message(
                chat_id=chat_id,
                text=_FRIENDLY_ERROR_TEXT,
                reply_markup=build_page_keyboard(back_target="main"),
            )
        except Exception:
            logger.exception("handler.error_notification_failed", chat_id=chat_id)

    return True
