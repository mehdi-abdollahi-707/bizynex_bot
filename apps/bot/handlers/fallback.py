"""Catches free-text messages that don't match any command or active flow.

Filtered by `StateFilter(None)` so it never intercepts input while a
stateful flow (estimator/request form, Phases 6-7) is waiting on the
customer's next answer — it only fires for genuinely unrecognized input,
and nudges the customer back to the button-driven menu.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message

from apps.bot.keyboards.main_menu import build_main_menu_keyboard

router = Router(name="fallback")


@router.message(StateFilter(None))
async def handle_unrecognized_message(message: Message) -> None:
    await message.answer(
        "متوجه پیام شما نشدم 🙏\nلطفاً از دکمه‌های زیر برای ادامه استفاده کنید:",
        reply_markup=build_main_menu_keyboard(),
    )
