"""Sanity checks on the Persian copy itself — catches accidental truncation
or a broken personalization placeholder, not meant to police prose style.
"""

from apps.bot.content.faq import FAQ_ITEMS, FAQ_TEXT
from apps.bot.content.main_menu import render_welcome_text


def test_welcome_text_is_personalized() -> None:
    assert "علی" in render_welcome_text("علی")


def test_welcome_text_escapes_a_malicious_display_name() -> None:
    # A Telegram first name is a free-text profile field we don't control —
    # under the bot's HTML parse mode, an unescaped tag here could break
    # message delivery or render a live link.
    text = render_welcome_text('<a href="http://evil.example.com">علی</a>')
    assert "<a" not in text
    assert "&lt;a" in text


def test_faq_text_contains_every_question_and_answer() -> None:
    for question, answer in FAQ_ITEMS:
        assert question in FAQ_TEXT
        assert answer in FAQ_TEXT


def test_exactly_four_faq_items_from_spec() -> None:
    assert len(FAQ_ITEMS) == 4
