"""Estimator keyboards must be fully wired: every service reachable, every
question page carrying working back/home controls.
"""

from apps.bot.keyboards.callback_data import (
    EstimatorAnswerCallback,
    EstimatorBackCallback,
    EstimatorStartCallback,
    NavCallback,
    RequestFormStartCallback,
)
from apps.bot.keyboards.estimator import (
    build_estimator_intro_rows,
    build_question_keyboard,
    build_result_keyboard,
    build_start_estimate_row,
)
from core.domain.estimator.config import ESTIMATOR_CONFIGS
from core.domain.value_objects.service_type import ServiceType


def test_intro_rows_cover_every_service_exactly_once() -> None:
    services = [
        EstimatorStartCallback.unpack(button.callback_data).service
        for row in build_estimator_intro_rows()
        for button in row
    ]
    assert set(services) == {s.value for s in ServiceType}
    assert len(services) == len(set(services))


def test_start_estimate_row_targets_the_given_service() -> None:
    (button,) = build_start_estimate_row(ServiceType.TELEGRAM_BOT)
    assert EstimatorStartCallback.unpack(button.callback_data).service == "telegram_bot"


def test_question_keyboard_has_one_button_per_option_plus_nav_row() -> None:
    question = ESTIMATOR_CONFIGS[ServiceType.WORDPRESS_WEBSITE].questions[0]  # 6 long-label options
    keyboard = build_question_keyboard(question)

    *option_rows, nav_row = keyboard.inline_keyboard
    option_buttons = [button for row in option_rows for button in row]
    assert len(option_buttons) == len(question.options)

    packed_options = {
        EstimatorAnswerCallback.unpack(b.callback_data).option for b in option_buttons
    }
    assert packed_options == {opt.key for opt in question.options}

    back_button, home_button = nav_row
    assert EstimatorBackCallback.unpack(back_button.callback_data) == EstimatorBackCallback()
    assert NavCallback.unpack(home_button.callback_data) == NavCallback(target="main")


def test_short_yes_no_options_pack_two_per_row() -> None:
    question = ESTIMATOR_CONFIGS[ServiceType.WORDPRESS_WEBSITE].questions[1]  # بله/خیر
    keyboard = build_question_keyboard(question)
    option_row = keyboard.inline_keyboard[0]
    assert len(option_row) == 2


def test_answer_callback_carries_the_question_key() -> None:
    question = ESTIMATOR_CONFIGS[ServiceType.POSTER_DESIGN].questions[0]
    keyboard = build_question_keyboard(question)
    first_button = keyboard.inline_keyboard[0][0]
    unpacked = EstimatorAnswerCallback.unpack(first_button.callback_data)
    assert unpacked.question == question.key


def test_result_keyboard_offers_request_form_linked_to_the_estimation() -> None:
    keyboard = build_result_keyboard(estimation_id=42)
    request_button, home_row = keyboard.inline_keyboard

    request_callback = RequestFormStartCallback.unpack(request_button[0].callback_data)
    assert request_callback.estimation_id == 42

    assert NavCallback.unpack(home_row[0].callback_data) == NavCallback(target="main")


def test_result_keyboard_omits_request_form_when_estimation_id_is_none() -> None:
    keyboard = build_result_keyboard(estimation_id=None)
    assert len(keyboard.inline_keyboard) == 1
    assert NavCallback.unpack(keyboard.inline_keyboard[0][0].callback_data) == NavCallback(
        target="main"
    )
