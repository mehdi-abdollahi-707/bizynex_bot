"""Direct handler-level tests for `show_main_menu`/`show_page` — the two
handlers behind nearly every page transition in the bot.
"""

from __future__ import annotations

from apps.bot.handlers import navigation
from apps.bot.keyboards.callback_data import NavCallback
from apps.bot.pages.registry import PAGES
from apps.bot.states.estimator import EstimatorFlow


async def test_show_main_menu_renders_the_personalized_welcome(
    make_state, make_callback, fake_customer
):
    state = make_state()
    callback = make_callback()

    await navigation.show_main_menu(callback, state, fake_customer)

    text = callback.message.edit_text.call_args.args[0]
    assert fake_customer.first_name in text
    assert "Bizynex" in text
    callback.answer.assert_awaited_once()


async def test_show_main_menu_clears_any_in_progress_flow(make_state, make_callback, fake_customer):
    state = make_state()
    await state.set_state(EstimatorFlow.answering)
    await state.update_data(service_type="wordpress_website", question_index=3, answers={})

    await navigation.show_main_menu(make_callback(), state, fake_customer)

    assert await state.get_state() is None
    assert await state.get_data() == {}


async def test_show_page_renders_a_registered_page(make_state, make_callback, fake_customer):
    callback = make_callback()

    await navigation.show_page(callback, NavCallback(target="about"), fake_customer)

    text = callback.message.edit_text.call_args.args[0]
    assert text == PAGES["about"].text
    callback.answer.assert_awaited_once()


async def test_show_page_rejects_an_unregistered_target(make_callback, fake_customer):
    callback = make_callback()

    await navigation.show_page(callback, NavCallback(target="not-a-real-page"), fake_customer)

    callback.message.edit_text.assert_not_awaited()
    callback.answer.assert_awaited_once()
    alert_text = callback.answer.call_args.args[0]
    assert "در دسترس نیست" in alert_text
