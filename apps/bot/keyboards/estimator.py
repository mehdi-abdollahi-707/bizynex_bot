"""Buttons for the estimator flow: service picker, question options, and result."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from apps.bot.keyboards.callback_data import (
    EstimatorAnswerCallback,
    EstimatorBackCallback,
    EstimatorStartCallback,
    NavCallback,
    RequestFormStartCallback,
)
from core.domain.estimator.question import EstimatorQuestion
from core.domain.value_objects.service_type import ServiceType

_SHORT_LABEL_MAX_LEN = 6  # e.g. "بله"/"خیر" — pack two per row; longer options get one per row


def build_estimator_intro_rows() -> list[list[InlineKeyboardButton]]:
    buttons = [
        InlineKeyboardButton(
            text=service_type.label_fa,
            callback_data=EstimatorStartCallback(service=service_type.value).pack(),
        )
        for service_type in ServiceType
    ]
    return [buttons[i : i + 2] for i in range(0, len(buttons), 2)]


def build_start_estimate_row(service_type: ServiceType) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text="💰 شروع برآورد قیمت",
            callback_data=EstimatorStartCallback(service=service_type.value).pack(),
        )
    ]


def build_question_keyboard(question: EstimatorQuestion) -> InlineKeyboardMarkup:
    option_buttons = [
        InlineKeyboardButton(
            text=option.label_fa,
            callback_data=EstimatorAnswerCallback(question=question.key, option=option.key).pack(),
        )
        for option in question.options
    ]

    if all(len(option.label_fa) <= _SHORT_LABEL_MAX_LEN for option in question.options):
        rows = [option_buttons[i : i + 2] for i in range(0, len(option_buttons), 2)]
    else:
        rows = [[button] for button in option_buttons]

    rows.append(
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data=EstimatorBackCallback().pack()),
            InlineKeyboardButton(text="🏠 خانه", callback_data=NavCallback(target="main").pack()),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_result_keyboard(estimation_id: int | None) -> InlineKeyboardMarkup:
    """`estimation_id` is None when persisting the estimation failed —
    in that case there's nothing for a request form to link to, so the
    "ثبت درخواست" button is omitted rather than leading to a broken flow.
    """
    rows: list[list[InlineKeyboardButton]] = []
    if estimation_id is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text="📝 ثبت درخواست پروژه",
                    callback_data=RequestFormStartCallback(estimation_id=estimation_id).pack(),
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(text="🏠 خانه", callback_data=NavCallback(target="main").pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
