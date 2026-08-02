"""The root main-menu keyboard (6 services, 2 per row)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from apps.bot.keyboards.callback_data import NavCallback

_MAIN_MENU_BUTTONS: list[tuple[str, str]] = [
    ("🏢 درباره Bizynex", "about"),
    ("💼 خدمات ما", "services"),
    ("💰 برآورد قیمت پروژه", "estimator"),
    ("📂 نمونه کارها", "portfolio"),
    ("❓ سوالات متداول", "faq"),
    ("📞 ارتباط با ما", "contact"),
]


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=text, callback_data=NavCallback(target=target).pack())
        for text, target in _MAIN_MENU_BUTTONS
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)
