"""Every main-menu button must resolve to a registered, non-empty page."""

from apps.bot.keyboards.main_menu import _MAIN_MENU_BUTTONS
from apps.bot.pages.registry import PAGES


def test_every_main_menu_target_is_registered() -> None:
    main_menu_targets = {target for _text, target in _MAIN_MENU_BUTTONS}
    assert main_menu_targets <= PAGES.keys()


def test_every_page_has_non_empty_text() -> None:
    for page_id, page in PAGES.items():
        assert page.text.strip(), f"page '{page_id}' has empty text"


def test_every_page_back_target_is_navigable() -> None:
    # back_target is either "main" (always valid) or another registered page.
    for page_id, page in PAGES.items():
        assert page.back_target == "main" or page.back_target in PAGES, page_id
