"""Persian copy for the "سوالات متداول" page."""

from __future__ import annotations

FAQ_ITEMS: list[tuple[str, str]] = [
    ("آیا قرارداد دارید؟", "بله، پیش از شروع پروژه قرارداد تنظیم می‌شود."),
    ("آیا پشتیبانی ارائه می‌دهید؟", "بله، تمام پروژه‌ها دارای پشتیبانی هستند."),
    ("آیا امکان پرداخت اقساطی وجود دارد؟", "خیر، در حال حاضر پرداخت اقساطی نداریم."),
    ("آیا نمونه‌کار دارید؟", "بله، نمونه‌کارها قابل مشاهده هستند."),
]


def _render() -> str:
    lines = ["❓ <b>سوالات متداول</b>", ""]
    for question, answer in FAQ_ITEMS:
        lines.append(f"▫️ <b>{question}</b>")
        lines.append(answer)
        lines.append("")
    return "\n".join(lines).rstrip()


FAQ_TEXT = _render()
