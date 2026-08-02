"""Lightweight validation for the project request form's free-text fields.

Unlike `PhoneNumber`, these aren't strict value objects — they're soft UX
guards against obviously-unusable input (empty, absurdly long, a single
word where a full name was asked for), not deep business rules. Each
function returns a Persian error message to show the customer, or `None`
if the input is acceptable.
"""

from __future__ import annotations

_MAX_TEXT_LENGTH = 1000


def validate_full_name(value: str) -> str | None:
    value = value.strip()
    if len(value) < 3:
        return "نام وارد شده خیلی کوتاه است. لطفاً نام و نام خانوادگی کامل را وارد کنید."
    if len(value.split()) < 2:
        return "لطفاً نام و نام خانوادگی خود را کامل وارد کنید (مثال: علی محمدی)."
    if len(value) > 100:
        return "نام وارد شده خیلی طولانی است."
    return None


def validate_company_name(value: str) -> str | None:
    value = value.strip()
    if not value:
        return "لطفاً نام شرکت را وارد کنید یا در صورت نداشتن، از دکمه «رد کردن» استفاده کنید."
    if len(value) > 200:
        return "نام شرکت وارد شده خیلی طولانی است (حداکثر 200 کاراکتر)."
    return None


def validate_project_description(value: str) -> str | None:
    value = value.strip()
    if len(value) < 10:
        return "لطفاً توضیحات کامل‌تری درباره پروژه خود بنویسید (حداقل چند جمله)."
    if len(value) > _MAX_TEXT_LENGTH:
        return f"توضیحات وارد شده خیلی طولانی است (حداکثر {_MAX_TEXT_LENGTH} کاراکتر)."
    return None


def validate_short_text(value: str, *, field_label_fa: str) -> str | None:
    value = value.strip()
    if not value:
        return f"لطفاً {field_label_fa} را وارد کنید."
    if len(value) > _MAX_TEXT_LENGTH:
        return f"متن وارد شده خیلی طولانی است (حداکثر {_MAX_TEXT_LENGTH} کاراکتر)."
    return None
