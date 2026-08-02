"""`safe()` must neutralize Telegram HTML markup characters without
mangling ordinary Persian text.
"""

from apps.bot.content.formatting import safe


def test_escapes_angle_brackets_and_ampersand() -> None:
    assert safe("<b>hi</b> & bye") == "&lt;b&gt;hi&lt;/b&gt; &amp; bye"


def test_neutralizes_a_forged_link_tag() -> None:
    malicious = '<a href="http://evil.example.com">کلیک کنید</a>'
    result = safe(malicious)
    assert "<a" not in result
    assert "&lt;a" in result


def test_leaves_ordinary_persian_text_unchanged() -> None:
    text = "می‌خواهم یک فروشگاه اینترنتی راه‌اندازی کنم."
    assert safe(text) == text


def test_leaves_quotes_unescaped() -> None:
    assert safe('او گفت "سلام"') == 'او گفت "سلام"'
