"""The /start command: greet the customer and show the main menu."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from apps.bot.content.main_menu import render_welcome_text
from apps.bot.keyboards.main_menu import build_main_menu_keyboard
from core.domain.entities.customer import Customer

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext, customer: Customer) -> None:
    # /start always resets — it's the customer's universal escape hatch out
    # of any in-progress flow (estimator, request form, ...).
    await state.clear()

    await message.answer(
        render_welcome_text(customer.display_name),
        reply_markup=build_main_menu_keyboard(),
    )
