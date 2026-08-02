"""Shared text-safety helper for Telegram HTML-parse-mode messages.

Every bot message is sent under a bot-wide default of ParseMode.HTML (see
`core.infrastructure.telegram.bot_factory`), so any text interpolated into
a message — including fields we don't control, like a customer's Telegram
first name or their own free-text answers — must be HTML-escaped first.
An unescaped '<', '>', or '&' can break message parsing entirely
(Telegram rejects the `sendMessage`/`editMessageText` call), or let
user-supplied text render as a live `<a href="...">` link in front of
whoever reads the message — including the admin notification.
"""

from __future__ import annotations

from html import escape as _escape_html


def safe(text: str) -> str:
    """Escape `&`, `<`, `>` — the characters Telegram's HTML parser treats
    as markup. Quotes are left alone: they aren't special outside of tag
    attribute values (which we never build from user input), and escaping
    them would make ordinary Persian punctuation look wrong in the chat.
    """
    return _escape_html(text, quote=False)
