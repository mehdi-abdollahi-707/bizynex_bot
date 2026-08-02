"""Persian copy for the estimator flow: the service picker, each question,
and the final result."""

from __future__ import annotations

from core.domain.estimator.calculator import EstimationResult
from core.domain.estimator.question import EstimatorQuestion

ESTIMATOR_INTRO_TEXT = (
    "💰 <b>برآورد قیمت پروژه</b>\n\n"
    "برای دریافت برآورد اولیه قیمت و زمان اجرا، ابتدا خدمت موردنظر خود را انتخاب "
    "کنید. سپس با پاسخ به چند سوال کوتاه، محدوده قیمت و زمان تقریبی پروژه شما "
    "محاسبه می‌شود 👇"
)

DISCLAIMER_TEXT = (
    "این مبلغ تنها یک برآورد اولیه است و پس از بررسی دقیق نیازهای پروژه، قیمت "
    "نهایی اعلام خواهد شد."
)


def render_question_text(question: EstimatorQuestion, *, index: int, total: int) -> str:
    return f"({index + 1}/{total}) {question.prompt_fa}"


def render_result_text(result: EstimationResult) -> str:
    return (
        "💰 <b>برآورد اولیه هزینه</b>\n"
        f"{result.price_range.format_fa()}\n\n"
        "⏳ <b>زمان تقریبی اجرا</b>\n"
        f"{result.duration_range.format_fa()}\n\n"
        f"{DISCLAIMER_TEXT}"
    )
