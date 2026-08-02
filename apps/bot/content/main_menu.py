"""Persian copy for the welcome / main-menu screen."""

from __future__ import annotations

from apps.bot.content.formatting import safe


def render_welcome_text(first_name: str) -> str:
    return (
        f"سلام {safe(first_name)} عزیز 👋 به Bizynex خوش آمدید!\n\n"
        "من دستیار هوشمند فروش Bizynex هستم و اینجا هستم تا شما را در مسیر انتخاب "
        "بهترین خدمات دیجیتال همراهی کنم.\n\n"
        "از منوی زیر بخش موردنظر خود را انتخاب کنید 👇"
    )


COMING_SOON_TEXT = "🚧 این بخش به‌زودی تکمیل می‌شود."
