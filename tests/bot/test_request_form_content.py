"""Request form copy: the summary must reflect collected data, and the
admin notification must contain every submitted field per spec.
"""

from apps.bot.content.request_form import (
    FIELD_LABELS_FA,
    FIELD_ORDER,
    FIELD_PROMPTS_FA,
    SKIPPABLE_FIELDS,
    render_admin_notification,
    render_summary_text,
)
from core.domain.entities.customer import Customer
from core.domain.entities.estimation import Estimation
from core.domain.entities.project_request import ProjectRequest
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType


def test_every_field_has_a_label_and_prompt() -> None:
    for field in FIELD_ORDER:
        assert field in FIELD_LABELS_FA
        assert field in FIELD_PROMPTS_FA


def test_only_company_name_and_attachment_are_skippable() -> None:
    assert SKIPPABLE_FIELDS == {"company_name", "attachment"}


def test_summary_shows_dash_for_missing_optional_fields() -> None:
    text = render_summary_text(
        {
            "full_name": "علی محمدی",
            "phone_number": "09123456789",
            "company_name": None,
            "project_description": "یک فروشگاه اینترنتی می‌خواهم.",
            "proposed_budget": "حدود ۵۰ میلیون",
            "desired_timeline": "۲ ماه",
            "attachment": None,
        }
    )
    assert "علی محمدی" in text
    assert "09123456789" in text
    assert "ندارد" in text  # company + attachment both absent
    assert "آیا اطلاعات بالا صحیح است؟" in text


def test_summary_shows_attachment_sent_when_present() -> None:
    text = render_summary_text(
        {
            "full_name": "علی محمدی",
            "phone_number": "09123456789",
            "company_name": "شرکت نمونه",
            "project_description": "توضیحات پروژه نمونه است.",
            "proposed_budget": "۱۰ میلیون",
            "desired_timeline": "۱ ماه",
            "attachment": {"kind": "document", "telegram_file_id": "abc"},
        }
    )
    assert "شرکت نمونه" in text
    assert "ارسال شد" in text


def test_admin_notification_contains_every_submitted_field() -> None:
    customer = Customer(telegram_id=123, first_name="علی", username="ali_m")
    estimation = Estimation(
        customer_id=1,
        service_type=ServiceType.WORDPRESS_WEBSITE,
        answers={},
        price_range=PriceRange(25_000_000, 120_000_000),
        duration_range=DurationRange(21, 49),
    )
    project_request = ProjectRequest(
        customer_id=1,
        estimation_id=7,
        full_name="علی محمدی",
        phone_number="09123456789",
        company_name="شرکت نمونه",
        project_description="یک فروشگاه اینترنتی می‌خواهم راه‌اندازی کنم.",
        proposed_budget="۵۰ میلیون تومان",
        desired_timeline="۲ ماه",
    )

    text = render_admin_notification(
        customer=customer,
        estimation=estimation,
        project_request=project_request,
        has_attachment=True,
    )

    assert "علی محمدی" in text
    assert "09123456789" in text
    assert "شرکت نمونه" in text
    assert "یک فروشگاه اینترنتی می‌خواهم راه‌اندازی کنم." in text
    assert "۵۰ میلیون تومان" in text
    assert "۲ ماه" in text
    assert "دارد" in text  # attachment indicator
    assert "123" in text  # telegram id
    assert "@ali_m" in text
    assert estimation.service_type.label_fa in text
    assert estimation.price_range.format_fa() in text


def test_summary_escapes_html_in_free_text_fields() -> None:
    text = render_summary_text(
        {
            "full_name": "علی محمدی",
            "phone_number": "09123456789",
            "company_name": '<a href="http://evil.example.com">شرکت</a>',
            "project_description": "توضیحات <script>alert(1)</script> پروژه",
            "proposed_budget": "۱۰ میلیون",
            "desired_timeline": "۱ ماه",
            "attachment": None,
        }
    )
    assert "<a href" not in text
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_admin_notification_escapes_html_in_project_request_fields() -> None:
    customer = Customer(telegram_id=123, first_name="علی", username=None)
    project_request = ProjectRequest(
        customer_id=1,
        estimation_id=7,
        full_name='<a href="http://evil.example.com">علی</a>',
        phone_number="09123456789",
        project_description="توضیحات.",
        proposed_budget="۱۰ میلیون",
        desired_timeline="۱ ماه",
    )

    text = render_admin_notification(
        customer=customer, estimation=None, project_request=project_request, has_attachment=False
    )

    assert "<a href" not in text
    assert "&lt;a href" in text


def test_admin_notification_handles_missing_estimation_gracefully() -> None:
    customer = Customer(telegram_id=123, first_name="علی", username=None)
    project_request = ProjectRequest(
        customer_id=1,
        estimation_id=7,
        full_name="علی محمدی",
        phone_number="09123456789",
        project_description="توضیحات.",
        proposed_budget="۱۰ میلیون",
        desired_timeline="۱ ماه",
    )

    text = render_admin_notification(
        customer=customer, estimation=None, project_request=project_request, has_attachment=False
    )

    assert "علی محمدی" in text
    assert "یوزرنیم: ندارد" in text
