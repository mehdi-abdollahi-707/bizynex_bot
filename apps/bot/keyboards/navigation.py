"""The 🔙 بازگشت / 🏠 خانه row every non-root page carries, plus optional
page-specific rows (e.g. the services list's service buttons) placed above it.
"""

from __future__ import annotations

from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from apps.bot.keyboards.callback_data import NavCallback


def build_page_keyboard(
    back_target: str,
    extra_rows: Sequence[Sequence[InlineKeyboardButton]] = (),
) -> InlineKeyboardMarkup:
    rows = [list(row) for row in extra_rows]
    rows.append(
        [
            InlineKeyboardButton(
                text="🔙 بازگشت", callback_data=NavCallback(target=back_target).pack()
            ),
            InlineKeyboardButton(text="🏠 خانه", callback_data=NavCallback(target="main").pack()),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
