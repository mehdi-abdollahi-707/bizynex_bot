"""Direct handler-level tests for /start and the unrecognized-message fallback."""

from __future__ import annotations

from apps.bot.handlers import fallback, start
from apps.bot.states.estimator import EstimatorFlow


async def test_start_shows_the_personalized_welcome(make_state, make_message, fake_customer):
    state = make_state()
    message = make_message("/start")

    await start.handle_start(message, state, fake_customer)

    text = message.answer.call_args.args[0]
    assert fake_customer.first_name in text
    assert "Bizynex" in text


async def test_start_clears_any_in_progress_flow(make_state, make_message, fake_customer):
    state = make_state()
    await state.set_state(EstimatorFlow.answering)
    await state.update_data(service_type="wordpress_website", question_index=2, answers={})

    await start.handle_start(make_message("/start"), state, fake_customer)

    assert await state.get_state() is None
    assert await state.get_data() == {}


async def test_fallback_nudges_toward_the_main_menu(make_message):
    message = make_message("something random")

    await fallback.handle_unrecognized_message(message)

    text = message.answer.call_args.args[0]
    assert "متوجه پیام شما نشدم" in text
    message.answer.assert_awaited_once()
