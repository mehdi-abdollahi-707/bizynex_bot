"""Drives the estimator's multi-question FSM flow.

Progress lives in FSM data (`service_type`, `question_index`, `answers`),
not in the state name — see `apps.bot.states.estimator` for why. Actual
pricing logic never appears here: this module only asks questions,
collects answers, and calls into `core.domain.estimator` to compute the
result.
"""

from __future__ import annotations

import structlog
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from apps.bot.content.estimator import render_question_text, render_result_text
from apps.bot.content.main_menu import render_welcome_text
from apps.bot.keyboards.callback_data import (
    EstimatorAnswerCallback,
    EstimatorBackCallback,
    EstimatorStartCallback,
)
from apps.bot.keyboards.estimator import build_question_keyboard, build_result_keyboard
from apps.bot.keyboards.main_menu import build_main_menu_keyboard
from apps.bot.states.estimator import EstimatorFlow
from core.domain.entities.customer import Customer
from core.domain.entities.estimation import Estimation
from core.domain.estimator.calculator import calculate_estimate
from core.domain.estimator.config import ESTIMATOR_CONFIGS
from core.domain.value_objects.service_type import ServiceType
from core.infrastructure.repositories.django_estimation_repository import (
    DjangoEstimationRepository,
)
from core.infrastructure.telegram.user_locks import get_user_lock

logger = structlog.get_logger("bizynex")

router = Router(name="estimator")

_estimation_repository = DjangoEstimationRepository()


async def _render_question(
    message: Message, service_type: ServiceType, question_index: int
) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    question = config.questions[question_index]
    await message.edit_text(
        render_question_text(question, index=question_index, total=len(config.questions)),
        reply_markup=build_question_keyboard(question),
    )


@router.callback_query(EstimatorStartCallback.filter())
async def start_estimator(
    callback: CallbackQuery, callback_data: EstimatorStartCallback, state: FSMContext
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    service_type = ServiceType(callback_data.service)

    await state.set_state(EstimatorFlow.answering)
    await state.update_data(service_type=service_type.value, question_index=0, answers={})

    await _render_question(callback.message, service_type, question_index=0)
    await callback.answer()


@router.callback_query(EstimatorFlow.answering, EstimatorAnswerCallback.filter())
async def handle_answer(
    callback: CallbackQuery,
    callback_data: EstimatorAnswerCallback,
    state: FSMContext,
    customer: Customer,
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    data = await state.get_data()
    service_type = ServiceType(data["service_type"])
    config = ESTIMATOR_CONFIGS[service_type]
    question_index = data["question_index"]
    current_question = config.questions[question_index]

    if callback_data.question != current_question.key:
        # Stale button press from a question the flow has already moved past.
        await callback.answer()
        return

    answers = dict(data["answers"])
    answers[current_question.key] = callback_data.option
    next_index = question_index + 1

    if next_index >= len(config.questions):
        # Guards against a fast double-tap on the final answer creating two
        # Estimation rows — see core.infrastructure.telegram.user_locks.
        lock = get_user_lock(customer.telegram_id)
        if lock.locked():
            await callback.answer()
            return
        async with lock:
            await _finish_estimation(callback.message, state, customer, service_type, answers)
    else:
        await state.update_data(question_index=next_index, answers=answers)
        await _render_question(callback.message, service_type, next_index)

    await callback.answer()


@router.callback_query(EstimatorFlow.answering, EstimatorBackCallback.filter())
async def handle_back(callback: CallbackQuery, state: FSMContext, customer: Customer) -> None:
    if callback.message is None:
        await callback.answer()
        return

    data = await state.get_data()
    question_index = data["question_index"]

    if question_index == 0:
        # Nothing to go back to — behave like cancel.
        await state.clear()
        await callback.message.edit_text(
            render_welcome_text(customer.display_name),
            reply_markup=build_main_menu_keyboard(),
        )
        await callback.answer()
        return

    service_type = ServiceType(data["service_type"])
    config = ESTIMATOR_CONFIGS[service_type]
    previous_index = question_index - 1
    previous_question = config.questions[previous_index]

    answers = dict(data["answers"])
    answers.pop(previous_question.key, None)

    await state.update_data(question_index=previous_index, answers=answers)
    await _render_question(callback.message, service_type, previous_index)
    await callback.answer()


async def _finish_estimation(
    message: Message,
    state: FSMContext,
    customer: Customer,
    service_type: ServiceType,
    answers: dict[str, str],
) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    result = calculate_estimate(config, answers)

    estimation_id: int | None = None
    try:
        created = await _estimation_repository.create(
            Estimation(
                customer_id=customer.id,
                service_type=service_type,
                answers=answers,
                price_range=result.price_range,
                duration_range=result.duration_range,
            )
        )
        estimation_id = created.id
        logger.info(
            "estimation.computed",
            customer_id=customer.id,
            service_type=service_type.value,
            price_min=result.price_range.min_toman,
            price_max=result.price_range.max_toman,
        )
    except Exception:
        # Showing the customer their estimate must not depend on a
        # successful DB write — log and continue. Without a persisted
        # estimation_id, the result keyboard omits "ثبت درخواست پروژه"
        # (see build_result_keyboard) since there'd be nothing for a
        # request to link to.
        logger.exception(
            "estimation.persist_failed", customer_id=customer.id, service_type=service_type.value
        )

    await state.clear()
    await message.edit_text(
        render_result_text(result), reply_markup=build_result_keyboard(estimation_id)
    )
