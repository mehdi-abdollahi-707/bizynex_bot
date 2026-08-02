"""Buttons for the project request form: per-field prompts, the summary
screen, and the edit-field menu.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from apps.bot.content.request_form import FIELD_LABELS_FA, FIELD_ORDER, SKIPPABLE_FIELDS
from apps.bot.keyboards.callback_data import (
    NavCallback,
    RequestFormConfirmCallback,
    RequestFormEditFieldCallback,
    RequestFormSkipCallback,
)

_HOME_BUTTON = InlineKeyboardButton(text="🏠 خانه", callback_data=NavCallback(target="main").pack())


def build_field_keyboard(field: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if field in SKIPPABLE_FIELDS:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⏭ رد کردن (ندارم)", callback_data=RequestFormSkipCallback().pack()
                )
            ]
        )
    rows.append([_HOME_BUTTON])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ ثبت درخواست",
                    callback_data=RequestFormConfirmCallback(action="submit").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ ویرایش",
                    callback_data=RequestFormConfirmCallback(action="edit").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ انصراف",
                    callback_data=RequestFormConfirmCallback(action="cancel").pack(),
                )
            ],
        ]
    )


def build_edit_field_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=FIELD_LABELS_FA[field],
            callback_data=RequestFormEditFieldCallback(field=field).pack(),
        )
        for field in FIELD_ORDER
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append(
        [
            InlineKeyboardButton(
                text="🔙 بازگشت به خلاصه",
                callback_data=RequestFormEditFieldCallback(field="__cancel__").pack(),
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
