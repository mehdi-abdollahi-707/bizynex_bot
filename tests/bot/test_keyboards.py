"""Keyboard builders must produce well-formed, fully wired inline keyboards."""

from apps.bot.keyboards.callback_data import NavCallback
from apps.bot.keyboards.main_menu import build_main_menu_keyboard
from apps.bot.keyboards.navigation import build_page_keyboard


def test_main_menu_has_six_buttons() -> None:
    keyboard = build_main_menu_keyboard()
    buttons = [button for row in keyboard.inline_keyboard for button in row]
    assert len(buttons) == 6


def test_main_menu_has_two_columns_per_row() -> None:
    keyboard = build_main_menu_keyboard()
    assert all(len(row) == 2 for row in keyboard.inline_keyboard)


def test_main_menu_targets_are_unique_and_navigable() -> None:
    keyboard = build_main_menu_keyboard()
    targets = [
        NavCallback.unpack(button.callback_data).target
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert len(targets) == len(set(targets))
    assert set(targets) == {"about", "services", "estimator", "portfolio", "faq", "contact"}


def test_page_keyboard_has_back_and_home_buttons() -> None:
    keyboard = build_page_keyboard(back_target="services")
    (row,) = keyboard.inline_keyboard
    back_button, home_button = row

    assert back_button.text == "🔙 بازگشت"
    assert NavCallback.unpack(back_button.callback_data).target == "services"

    assert home_button.text == "🏠 خانه"
    assert NavCallback.unpack(home_button.callback_data).target == "main"
