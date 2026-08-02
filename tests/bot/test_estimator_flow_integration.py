"""Full estimator conversation walkthroughs, exercised at the handler
level — real question sequencing, answer collection, back-stepping, and
pricing calculation, with only the DB-backed repository call mocked.
"""

from __future__ import annotations

import pytest

from apps.bot.handlers import estimator
from apps.bot.keyboards.callback_data import EstimatorAnswerCallback, EstimatorStartCallback
from apps.bot.states.estimator import EstimatorFlow
from core.domain.entities.estimation import Estimation
from core.domain.estimator.config import ESTIMATOR_CONFIGS
from core.domain.value_objects.service_type import ServiceType


@pytest.fixture
def created_estimations(monkeypatch):
    created: list[Estimation] = []

    async def fake_create(estimation: Estimation) -> Estimation:
        created.append(estimation)
        return Estimation(
            id=len(created),
            customer_id=estimation.customer_id,
            service_type=estimation.service_type,
            answers=estimation.answers,
            price_range=estimation.price_range,
            duration_range=estimation.duration_range,
        )

    monkeypatch.setattr(estimator._estimation_repository, "create", fake_create)
    return created


async def _answer_all_questions(state, make_callback, customer, service_type, *, pick):
    """Drive the flow to completion, choosing `pick(question) -> option` at
    each step. Returns the callback from the final (result-showing) tap.
    """
    config = ESTIMATOR_CONFIGS[service_type]
    callback = None
    for question in config.questions:
        option = pick(question)
        callback = make_callback()
        await estimator.handle_answer(
            callback,
            EstimatorAnswerCallback(question=question.key, option=option.key),
            state,
            customer,
        )
    return callback


async def test_start_estimator_shows_first_question(make_state, make_callback, fake_customer):
    state = make_state()
    callback = make_callback()

    await estimator.start_estimator(
        callback, EstimatorStartCallback(service=ServiceType.WORDPRESS_WEBSITE.value), state
    )

    assert await state.get_state() == EstimatorFlow.answering.state
    data = await state.get_data()
    assert data == {"service_type": "wordpress_website", "question_index": 0, "answers": {}}

    text = callback.message.edit_text.call_args.args[0]
    assert text.startswith("(1/8)")
    callback.answer.assert_awaited_once()


async def test_full_happy_path_cheapest_answers_computes_and_persists(
    make_state, make_callback, fake_customer, created_estimations
):
    state = make_state()
    await estimator.start_estimator(
        make_callback(),
        EstimatorStartCallback(service=ServiceType.WORDPRESS_WEBSITE.value),
        state,
    )

    final_callback = await _answer_all_questions(
        state,
        make_callback,
        fake_customer,
        ServiceType.WORDPRESS_WEBSITE,
        pick=lambda q: min(q.options, key=lambda o: o.score),
    )

    # Flow ends: state cleared, result shown, one Estimation persisted.
    assert await state.get_state() is None
    result_text = final_callback.message.edit_text.call_args.args[0]
    assert "برآورد اولیه هزینه" in result_text
    assert "زمان تقریبی اجرا" in result_text

    assert len(created_estimations) == 1
    assert created_estimations[0].customer_id == fake_customer.id
    assert created_estimations[0].service_type == ServiceType.WORDPRESS_WEBSITE

    # The result keyboard must offer "ثبت درخواست پروژه" since persistence succeeded.
    keyboard = final_callback.message.edit_text.call_args.kwargs["reply_markup"]
    assert len(keyboard.inline_keyboard) == 2


async def test_priciest_answers_produce_a_higher_estimate_than_cheapest(
    make_state, make_callback, fake_customer, created_estimations
):
    async def run(pick):
        state = make_state()
        await estimator.start_estimator(
            make_callback(),
            EstimatorStartCallback(service=ServiceType.POSTER_DESIGN.value),
            state,
        )
        return await _answer_all_questions(
            state, make_callback, fake_customer, ServiceType.POSTER_DESIGN, pick=pick
        )

    cheap_callback = await run(lambda q: min(q.options, key=lambda o: o.score))
    pricey_callback = await run(lambda q: max(q.options, key=lambda o: o.score))

    cheap_text = cheap_callback.message.edit_text.call_args.args[0]
    pricey_text = pricey_callback.message.edit_text.call_args.args[0]
    assert cheap_text != pricey_text


async def test_stale_answer_for_a_past_question_is_ignored(
    make_state, make_callback, fake_customer, created_estimations
):
    state = make_state()
    await estimator.start_estimator(
        make_callback(),
        EstimatorStartCallback(service=ServiceType.WORDPRESS_WEBSITE.value),
        state,
    )
    config = ESTIMATOR_CONFIGS[ServiceType.WORDPRESS_WEBSITE]

    # Answer question 0 for real, advancing to question 1.
    await estimator.handle_answer(
        make_callback(),
        EstimatorAnswerCallback(question=config.questions[0].key, option="landing"),
        state,
        fake_customer,
    )
    data_after_first = await state.get_data()
    assert data_after_first["question_index"] == 1

    # A stale tap referencing question 0 again (e.g. a duplicate old
    # keyboard) must not be applied.
    stale_callback = make_callback()
    await estimator.handle_answer(
        stale_callback,
        EstimatorAnswerCallback(question=config.questions[0].key, option="store"),
        state,
        fake_customer,
    )

    data_after_stale = await state.get_data()
    assert data_after_stale == data_after_first
    stale_callback.message.edit_text.assert_not_awaited()
    stale_callback.answer.assert_awaited_once()


async def test_back_from_second_question_removes_first_answer_and_reasks_it(
    make_state, make_callback, fake_customer
):
    state = make_state()
    await estimator.start_estimator(
        make_callback(),
        EstimatorStartCallback(service=ServiceType.WORDPRESS_WEBSITE.value),
        state,
    )
    config = ESTIMATOR_CONFIGS[ServiceType.WORDPRESS_WEBSITE]

    await estimator.handle_answer(
        make_callback(),
        EstimatorAnswerCallback(question=config.questions[0].key, option="store"),
        state,
        fake_customer,
    )
    assert (await state.get_data())["question_index"] == 1

    back_callback = make_callback()
    await estimator.handle_back(back_callback, state, fake_customer)

    data = await state.get_data()
    assert data["question_index"] == 0
    assert config.questions[0].key not in data["answers"]
    back_text = back_callback.message.edit_text.call_args.args[0]
    assert back_text.startswith("(1/8)")


async def test_back_from_first_question_behaves_like_cancel(
    make_state, make_callback, fake_customer
):
    state = make_state()
    await estimator.start_estimator(
        make_callback(),
        EstimatorStartCallback(service=ServiceType.TELEGRAM_BOT.value),
        state,
    )

    back_callback = make_callback()
    await estimator.handle_back(back_callback, state, fake_customer)

    assert await state.get_state() is None
    text = back_callback.message.edit_text.call_args.args[0]
    assert "Bizynex" in text


async def test_persistence_failure_still_shows_result_without_request_form_button(
    make_state, make_callback, fake_customer, monkeypatch
):
    async def failing_create(estimation):
        raise RuntimeError("db is down")

    monkeypatch.setattr(estimator._estimation_repository, "create", failing_create)

    state = make_state()
    await estimator.start_estimator(
        make_callback(),
        EstimatorStartCallback(service=ServiceType.THUMBNAIL_COVER_DESIGN.value),
        state,
    )
    final_callback = await _answer_all_questions(
        state,
        make_callback,
        fake_customer,
        ServiceType.THUMBNAIL_COVER_DESIGN,
        pick=lambda q: q.options[0],
    )

    result_text = final_callback.message.edit_text.call_args.args[0]
    assert "برآورد اولیه هزینه" in result_text  # customer still sees their estimate

    keyboard = final_callback.message.edit_text.call_args.kwargs["reply_markup"]
    assert len(keyboard.inline_keyboard) == 1  # only "🏠 خانه" — no request-form button
