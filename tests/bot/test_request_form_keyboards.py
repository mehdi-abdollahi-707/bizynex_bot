"""Request form keyboards: skip button only on skippable fields, all three
confirm actions present, every field reachable from the edit menu.
"""

from apps.bot.content.request_form import FIELD_ORDER, SKIPPABLE_FIELDS
from apps.bot.keyboards.callback_data import (
    NavCallback,
    RequestFormConfirmCallback,
    RequestFormEditFieldCallback,
    RequestFormSkipCallback,
)
from apps.bot.keyboards.request_form import (
    build_confirm_keyboard,
    build_edit_field_menu_keyboard,
    build_field_keyboard,
)


def test_skippable_fields_get_a_skip_button() -> None:
    for field in SKIPPABLE_FIELDS:
        keyboard = build_field_keyboard(field)
        first_row_callback = keyboard.inline_keyboard[0][0].callback_data
        assert RequestFormSkipCallback.unpack(first_row_callback) == RequestFormSkipCallback()


def test_non_skippable_fields_have_only_home_button() -> None:
    non_skippable = set(FIELD_ORDER) - SKIPPABLE_FIELDS
    for field in non_skippable:
        keyboard = build_field_keyboard(field)
        buttons = [b for row in keyboard.inline_keyboard for b in row]
        assert len(buttons) == 1
        assert NavCallback.unpack(buttons[0].callback_data) == NavCallback(target="main")


def test_confirm_keyboard_has_all_three_actions_in_spec_order() -> None:
    keyboard = build_confirm_keyboard()
    actions = [
        RequestFormConfirmCallback.unpack(row[0].callback_data).action
        for row in keyboard.inline_keyboard
    ]
    assert actions == ["submit", "edit", "cancel"]


def test_edit_menu_covers_every_field_plus_cancel() -> None:
    keyboard = build_edit_field_menu_keyboard()
    fields = [
        RequestFormEditFieldCallback.unpack(button.callback_data).field
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert set(FIELD_ORDER) <= set(fields)
    assert "__cancel__" in fields
