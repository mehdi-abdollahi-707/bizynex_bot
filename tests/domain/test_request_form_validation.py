"""Request form field validators: reject obviously-unusable input, accept
reasonable input, in Persian error messages.
"""

from core.application.request_form_validation import (
    validate_company_name,
    validate_full_name,
    validate_project_description,
    validate_short_text,
)


def test_full_name_rejects_single_word() -> None:
    assert validate_full_name("علی") is not None


def test_full_name_rejects_too_short() -> None:
    assert validate_full_name("اا") is not None


def test_full_name_accepts_two_words() -> None:
    assert validate_full_name("علی محمدی") is None


def test_full_name_rejects_absurdly_long() -> None:
    assert validate_full_name("علی " * 60) is not None


def test_project_description_rejects_too_short() -> None:
    assert validate_project_description("سلام") is not None


def test_project_description_accepts_reasonable_text() -> None:
    text = "می‌خواهم یک فروشگاه اینترنتی برای فروش لباس راه‌اندازی کنم."
    assert validate_project_description(text) is None


def test_short_text_rejects_empty() -> None:
    assert validate_short_text("   ", field_label_fa="بودجه پیشنهادی") is not None


def test_short_text_accepts_non_empty() -> None:
    assert validate_short_text("حدود ۱۰ میلیون تومان", field_label_fa="بودجه پیشنهادی") is None


def test_short_text_rejects_absurdly_long() -> None:
    assert validate_short_text("الف" * 500, field_label_fa="زمان موردنظر") is not None


def test_company_name_rejects_empty() -> None:
    assert validate_company_name("   ") is not None


def test_company_name_accepts_reasonable_text() -> None:
    assert validate_company_name("شرکت نمونه") is None


def test_company_name_rejects_absurdly_long() -> None:
    assert validate_company_name("الف" * 300) is not None
