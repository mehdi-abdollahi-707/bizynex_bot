"""Drives the project request form's FSM flow: 7 fields, a summary with
per-field editing, submission, and the admin notification.

Sequencing lives in `_proceed`/`_next_field`, shared by every field's
handler, so "what's the next field" and "are we mid-edit, so go straight
back to the summary instead" are each defined exactly once.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.conf import settings

from apps.bot.content.main_menu import render_welcome_text
from apps.bot.content.request_form import (
    EDIT_MENU_PROMPT,
    FIELD_ORDER,
    FIELD_PROMPTS_FA,
    INVALID_ESTIMATION_TEXT,
    SUBMISSION_ERROR_TEXT,
    SUBMISSION_SUCCESS_TEXT,
    render_admin_notification,
    render_summary_text,
)
from apps.bot.keyboards.callback_data import (
    RequestFormConfirmCallback,
    RequestFormEditFieldCallback,
    RequestFormSkipCallback,
    RequestFormStartCallback,
)
from apps.bot.keyboards.main_menu import build_main_menu_keyboard
from apps.bot.keyboards.request_form import (
    build_confirm_keyboard,
    build_edit_field_menu_keyboard,
    build_field_keyboard,
)
from apps.bot.states.request_form import RequestFormFlow
from core.application.request_form_validation import (
    validate_company_name,
    validate_full_name,
    validate_project_description,
    validate_short_text,
)
from core.domain.entities.attachment import ProjectAttachment
from core.domain.entities.customer import Customer
from core.domain.entities.project_request import ProjectRequest
from core.domain.value_objects.phone_number import PhoneNumber
from core.infrastructure.repositories.django_estimation_repository import (
    DjangoEstimationRepository,
)
from core.infrastructure.repositories.django_project_request_repository import (
    DjangoProjectRequestRepository,
)
from core.infrastructure.telegram.user_locks import get_user_lock

logger = structlog.get_logger("bizynex")

router = Router(name="request_form")

_estimation_repository = DjangoEstimationRepository()
_project_request_repository = DjangoProjectRequestRepository()

_STATE_BY_FIELD = {
    "full_name": RequestFormFlow.full_name,
    "phone_number": RequestFormFlow.phone_number,
    "company_name": RequestFormFlow.company_name,
    "project_description": RequestFormFlow.project_description,
    "proposed_budget": RequestFormFlow.proposed_budget,
    "desired_timeline": RequestFormFlow.desired_timeline,
    "attachment": RequestFormFlow.attachment,
}

SendFn = Callable[..., Awaitable[Any]]


def _next_field(current: str) -> str | None:
    index = FIELD_ORDER.index(current)
    return FIELD_ORDER[index + 1] if index + 1 < len(FIELD_ORDER) else None


async def _proceed(send: SendFn, state: FSMContext, *, current_field: str) -> None:
    """Store nothing itself — the caller already updated FSM data. Decides
    what happens next: back to the summary if this was an edit, otherwise
    the next field in sequence, or the summary if this was the last field.
    """
    data = await state.get_data()

    if data.get("editing"):
        await state.update_data(editing=False)
        await _render_confirm(send, state)
        return

    next_field = _next_field(current_field)
    if next_field is None:
        await _render_confirm(send, state)
        return

    await state.set_state(_STATE_BY_FIELD[next_field])
    await send(FIELD_PROMPTS_FA[next_field], reply_markup=build_field_keyboard(next_field))


async def _render_confirm(send: SendFn, state: FSMContext) -> None:
    await state.set_state(RequestFormFlow.confirm)
    data = await state.get_data()
    await send(render_summary_text(data), reply_markup=build_confirm_keyboard())


# --- Entry point -----------------------------------------------------------


@router.callback_query(RequestFormStartCallback.filter())
async def start_request_form(
    callback: CallbackQuery,
    callback_data: RequestFormStartCallback,
    state: FSMContext,
    customer: Customer,
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    # A forged or stale estimation_id (someone else's, or one that no
    # longer exists) must not silently attach this customer's request to
    # the wrong estimate — reject early rather than at final submission,
    # before they've spent time filling out the whole form.
    estimation = await _estimation_repository.get_by_id(callback_data.estimation_id)
    if estimation is None or estimation.customer_id != customer.id:
        logger.warning(
            "request_form.invalid_estimation_reference",
            customer_id=customer.id,
            estimation_id=callback_data.estimation_id,
        )
        await callback.message.edit_text(
            INVALID_ESTIMATION_TEXT, reply_markup=build_main_menu_keyboard()
        )
        await callback.answer()
        return

    await state.set_state(RequestFormFlow.full_name)
    await state.update_data(
        estimation_id=callback_data.estimation_id,
        editing=False,
        company_name=None,
        attachment=None,
    )

    await callback.message.edit_text(
        FIELD_PROMPTS_FA["full_name"], reply_markup=build_field_keyboard("full_name")
    )
    await callback.answer()


# --- Text fields -------------------------------------------------------------


@router.message(RequestFormFlow.full_name)
async def handle_full_name(message: Message, state: FSMContext) -> None:
    error = validate_full_name(message.text or "")
    if error:
        await message.answer(error)
        return
    await state.update_data(full_name=message.text.strip())
    await _proceed(message.answer, state, current_field="full_name")


@router.message(RequestFormFlow.phone_number)
async def handle_phone_number(message: Message, state: FSMContext) -> None:
    try:
        phone = PhoneNumber.parse(message.text or "")
    except ValueError:
        await message.answer(
            "شماره موبایل واردشده معتبر نیست. لطفاً یک شماره موبایل ایرانی معتبر وارد کنید "
            "(مثال: 09123456789)."
        )
        return
    await state.update_data(phone_number=phone.value)
    await _proceed(message.answer, state, current_field="phone_number")


@router.message(RequestFormFlow.company_name)
async def handle_company_name(message: Message, state: FSMContext) -> None:
    error = validate_company_name(message.text or "")
    if error:
        await message.answer(error)
        return
    await state.update_data(company_name=message.text.strip())
    await _proceed(message.answer, state, current_field="company_name")


@router.callback_query(RequestFormFlow.company_name, RequestFormSkipCallback.filter())
async def handle_skip_company_name(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return
    await state.update_data(company_name=None)
    await _proceed(callback.message.edit_text, state, current_field="company_name")
    await callback.answer()


@router.message(RequestFormFlow.project_description)
async def handle_project_description(message: Message, state: FSMContext) -> None:
    error = validate_project_description(message.text or "")
    if error:
        await message.answer(error)
        return
    await state.update_data(project_description=message.text.strip())
    await _proceed(message.answer, state, current_field="project_description")


@router.message(RequestFormFlow.proposed_budget)
async def handle_proposed_budget(message: Message, state: FSMContext) -> None:
    error = validate_short_text(message.text or "", field_label_fa="بودجه پیشنهادی")
    if error:
        await message.answer(error)
        return
    await state.update_data(proposed_budget=message.text.strip())
    await _proceed(message.answer, state, current_field="proposed_budget")


@router.message(RequestFormFlow.desired_timeline)
async def handle_desired_timeline(message: Message, state: FSMContext) -> None:
    error = validate_short_text(message.text or "", field_label_fa="زمان موردنظر")
    if error:
        await message.answer(error)
        return
    await state.update_data(desired_timeline=message.text.strip())
    await _proceed(message.answer, state, current_field="desired_timeline")


# --- Attachment (optional file) --------------------------------------------


@router.message(RequestFormFlow.attachment, F.document)
async def handle_attachment_document(message: Message, state: FSMContext) -> None:
    document = message.document
    await state.update_data(
        attachment={
            "kind": "document",
            "telegram_file_id": document.file_id,
            "telegram_file_unique_id": document.file_unique_id,
            "file_name": document.file_name,
            "mime_type": document.mime_type,
            "file_size": document.file_size,
        }
    )
    await _proceed(message.answer, state, current_field="attachment")


@router.message(RequestFormFlow.attachment, F.photo)
async def handle_attachment_photo(message: Message, state: FSMContext) -> None:
    largest = message.photo[-1]
    await state.update_data(
        attachment={
            "kind": "photo",
            "telegram_file_id": largest.file_id,
            "telegram_file_unique_id": largest.file_unique_id,
            "file_name": None,
            "mime_type": None,
            "file_size": largest.file_size,
        }
    )
    await _proceed(message.answer, state, current_field="attachment")


@router.callback_query(RequestFormFlow.attachment, RequestFormSkipCallback.filter())
async def handle_skip_attachment(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return
    await state.update_data(attachment=None)
    await _proceed(callback.message.edit_text, state, current_field="attachment")
    await callback.answer()


@router.message(RequestFormFlow.attachment)
async def handle_attachment_wrong_type(message: Message) -> None:
    await message.answer("لطفاً یک فایل ارسال کنید یا از دکمه «رد کردن» استفاده کنید.")


# --- Summary: submit / edit / cancel ---------------------------------------


@router.callback_query(
    RequestFormFlow.confirm, RequestFormConfirmCallback.filter(F.action == "edit")
)
async def show_edit_menu(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return
    await callback.message.edit_text(
        EDIT_MENU_PROMPT, reply_markup=build_edit_field_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(RequestFormFlow.confirm, RequestFormEditFieldCallback.filter())
async def handle_edit_field_choice(
    callback: CallbackQuery, callback_data: RequestFormEditFieldCallback, state: FSMContext
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    if callback_data.field == "__cancel__":
        await _render_confirm(callback.message.edit_text, state)
        await callback.answer()
        return

    field = callback_data.field
    await state.update_data(editing=True)
    await state.set_state(_STATE_BY_FIELD[field])
    await callback.message.edit_text(
        FIELD_PROMPTS_FA[field], reply_markup=build_field_keyboard(field)
    )
    await callback.answer()


@router.callback_query(
    RequestFormFlow.confirm, RequestFormConfirmCallback.filter(F.action == "cancel")
)
async def handle_cancel(callback: CallbackQuery, state: FSMContext, customer: Customer) -> None:
    if callback.message is None:
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(
        render_welcome_text(customer.display_name), reply_markup=build_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(
    RequestFormFlow.confirm, RequestFormConfirmCallback.filter(F.action == "submit")
)
async def handle_submit(
    callback: CallbackQuery, state: FSMContext, customer: Customer, bot: Bot
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    # Guards against a fast double-tap on "✅ ثبت درخواست" creating two
    # ProjectRequest rows (and two admin notifications) for one submission.
    lock = get_user_lock(customer.telegram_id)
    if lock.locked():
        await callback.answer()
        return

    async with lock:
        # Re-check: if the first tap of a double-tap already completed and
        # cleared the state before this one acquired the lock, there's
        # nothing left to submit.
        if await state.get_state() != RequestFormFlow.confirm.state:
            await callback.answer()
            return
        await _submit(callback, state, customer, bot)


async def _submit(callback: CallbackQuery, state: FSMContext, customer: Customer, bot: Bot) -> None:
    data = await state.get_data()

    try:
        created = await _project_request_repository.create(
            ProjectRequest(
                customer_id=customer.id,
                estimation_id=data["estimation_id"],
                full_name=data["full_name"],
                phone_number=data["phone_number"],
                company_name=data.get("company_name"),
                project_description=data["project_description"],
                proposed_budget=data["proposed_budget"],
                desired_timeline=data["desired_timeline"],
            )
        )

        attachment_data = data.get("attachment")
        if attachment_data:
            await _project_request_repository.add_attachment(
                ProjectAttachment(project_request_id=created.id, **attachment_data)
            )

        logger.info(
            "project_request.submitted", customer_id=customer.id, project_request_id=created.id
        )
    except Exception:
        logger.exception("project_request.persist_failed", customer_id=customer.id)
        await state.clear()
        await callback.message.edit_text(
            SUBMISSION_ERROR_TEXT, reply_markup=build_main_menu_keyboard()
        )
        await callback.answer()
        return

    await _notify_admin(
        bot, customer=customer, project_request=created, attachment_data=data.get("attachment")
    )

    await state.clear()
    await callback.message.edit_text(
        SUBMISSION_SUCCESS_TEXT, reply_markup=build_main_menu_keyboard()
    )
    await callback.answer()


async def _notify_admin(
    bot: Bot,
    *,
    customer: Customer,
    project_request: ProjectRequest,
    attachment_data: dict[str, Any] | None,
) -> None:
    """Best-effort — a failure here must not affect the customer's success response."""
    try:
        estimation = await _estimation_repository.get_by_id(project_request.estimation_id)
    except Exception:
        logger.exception(
            "admin_notification.estimation_lookup_failed",
            project_request_id=project_request.id,
        )
        estimation = None

    try:
        await bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=render_admin_notification(
                customer=customer,
                estimation=estimation,
                project_request=project_request,
                has_attachment=bool(attachment_data),
            ),
        )
        if attachment_data:
            file_id = attachment_data["telegram_file_id"]
            if attachment_data["kind"] == "photo":
                await bot.send_photo(chat_id=settings.ADMIN_ID, photo=file_id)
            else:
                await bot.send_document(chat_id=settings.ADMIN_ID, document=file_id)
    except Exception:
        logger.exception("admin_notification.send_failed", project_request_id=project_request.id)
