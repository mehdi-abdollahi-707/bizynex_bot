"""Generic handler powering every 🔙 بازگشت / 🏠 خانه / main-menu button.

Two handlers: `nav:main` is special-cased because the root menu has its own
keyboard shape (a 2-column grid, no nav row); everything else is looked up
in the page registry and rendered with the standard nav row.
"""

from __future__ import annotations

import structlog
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from apps.bot.content.main_menu import render_welcome_text
from apps.bot.keyboards.callback_data import NavCallback
from apps.bot.keyboards.main_menu import build_main_menu_keyboard
from apps.bot.keyboards.navigation import build_page_keyboard
from apps.bot.pages.registry import PAGES
from core.domain.entities.customer import Customer

logger = structlog.get_logger("bizynex")

router = Router(name="navigation")


@router.callback_query(NavCallback.filter(F.target == "main"))
async def show_main_menu(callback: CallbackQuery, state: FSMContext, customer: Customer) -> None:
    if callback.message is None:
        await callback.answer()
        return

    # Going home always abandons any in-progress flow (estimator, request
    # form, ...) — a stateful flow should never be resumable from a "🏠 خانه" tap.
    await state.clear()

    await callback.message.edit_text(
        render_welcome_text(customer.display_name),
        reply_markup=build_main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(NavCallback.filter())
async def show_page(
    callback: CallbackQuery, callback_data: NavCallback, customer: Customer
) -> None:
    page = PAGES.get(callback_data.target)
    if page is None or callback.message is None:
        await callback.answer("این بخش در دسترس نیست.", show_alert=True)
        return

    logger.info("page.viewed", target=callback_data.target, customer_id=customer.id)

    await callback.message.edit_text(
        page.text,
        reply_markup=build_page_keyboard(page.back_target, page.extra_rows),
    )
    await callback.answer()
