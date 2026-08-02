"""Buttons for the services list, service detail, and comparison pages."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton

from apps.bot.keyboards.callback_data import NavCallback
from core.domain.value_objects.service_type import ServiceType


def service_detail_target(service_type: ServiceType) -> str:
    # "-" not ":" — aiogram's CallbackData uses ":" as its own field
    # separator, so a value containing it would fail to pack.
    return f"service-{service_type.value}"


def _service_button(service_type: ServiceType) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=service_type.label_fa,
        callback_data=NavCallback(target=service_detail_target(service_type)).pack(),
    )


def build_services_list_rows() -> list[list[InlineKeyboardButton]]:
    buttons = [_service_button(service_type) for service_type in ServiceType]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append(
        [
            InlineKeyboardButton(
                text="🆚 مقایسه وردپرسی و اختصاصی",
                callback_data=NavCallback(target="compare_websites").pack(),
            )
        ]
    )
    return rows


def build_comparison_choice_rows() -> list[list[InlineKeyboardButton]]:
    return [
        [
            _service_button(ServiceType.WORDPRESS_WEBSITE),
            _service_button(ServiceType.CUSTOM_WEBSITE),
        ]
    ]


def build_website_service_extra_rows() -> list[list[InlineKeyboardButton]]:
    """The "🆚 مقایسه" shortcut shown on the WordPress and Custom website pages."""
    return [
        [
            InlineKeyboardButton(
                text="🆚 مقایسه دو گزینه",
                callback_data=NavCallback(target="compare_websites").pack(),
            )
        ]
    ]
