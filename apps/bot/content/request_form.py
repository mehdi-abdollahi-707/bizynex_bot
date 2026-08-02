"""Persian copy for the project request form: per-field prompts, the
summary shown before submission, and the admin notification.
"""

from __future__ import annotations

from typing import Any

from apps.bot.content.formatting import safe
from core.domain.entities.customer import Customer
from core.domain.entities.estimation import Estimation
from core.domain.entities.project_request import ProjectRequest

FIELD_ORDER: list[str] = [
    "full_name",
    "phone_number",
    "company_name",
    "project_description",
    "proposed_budget",
    "desired_timeline",
    "attachment",
]

FIELD_LABELS_FA: dict[str, str] = {
    "full_name": "نام و نام خانوادگی",
    "phone_number": "شماره موبایل",
    "company_name": "نام شرکت",
    "project_description": "توضیحات پروژه",
    "proposed_budget": "بودجه پیشنهادی",
    "desired_timeline": "زمان موردنظر",
    "attachment": "فایل پروژه",
}

FIELD_PROMPTS_FA: dict[str, str] = {
    "full_name": "لطفاً نام و نام خانوادگی خود را وارد کنید:",
    "phone_number": "لطفاً شماره موبایل خود را وارد کنید (مثال: 09123456789):",
    "company_name": "نام شرکت شما چیست؟ (اختیاری — در صورت نداشتن، دکمه زیر را بزنید)",
    "project_description": "لطفاً توضیحات پروژه خود را بنویسید:",
    "proposed_budget": "بودجه پیشنهادی شما برای این پروژه چقدر است؟",
    "desired_timeline": "زمان موردنظر شما برای تحویل پروژه چقدر است؟",
    "attachment": (
        "در صورت تمایل می‌توانید فایلی مرتبط با پروژه ارسال کنید "
        "(اختیاری — در صورت نداشتن، دکمه زیر را بزنید)"
    ),
}

SKIPPABLE_FIELDS = {"company_name", "attachment"}

EDIT_MENU_PROMPT = "کدام بخش را می‌خواهید ویرایش کنید؟"

SUBMISSION_SUCCESS_TEXT = (
    "✅ <b>درخواست شما با موفقیت ثبت شد!</b>\n\n"
    "همکاران ما در اسرع وقت درخواست شما را بررسی و با شما تماس خواهند گرفت.\n\n"
    "از اعتماد شما به Bizynex سپاسگزاریم 🌟"
)

SUBMISSION_ERROR_TEXT = (
    "⚠️ متأسفانه در ثبت درخواست شما مشکلی پیش آمد.\n\n"
    "لطفاً کمی بعد دوباره تلاش کنید یا از طریق بخش «📞 ارتباط با ما» با ما در تماس باشید."
)

INVALID_ESTIMATION_TEXT = (
    "⚠️ این برآورد قیمت دیگر معتبر نیست.\n\n"
    "لطفاً ابتدا از بخش «💰 برآورد قیمت پروژه» یک برآورد جدید دریافت کنید."
)


def render_summary_text(data: dict[str, Any]) -> str:
    attachment = data.get("attachment")
    company_name = data.get("company_name")
    lines = [
        "📋 <b>خلاصه درخواست شما</b>",
        "",
        f"👤 {FIELD_LABELS_FA['full_name']}: {safe(data.get('full_name', ''))}",
        f"📱 {FIELD_LABELS_FA['phone_number']}: {safe(data.get('phone_number', ''))}",
        f"🏢 {FIELD_LABELS_FA['company_name']}: {safe(company_name) if company_name else 'ندارد'}",
        f"📝 {FIELD_LABELS_FA['project_description']}: "
        f"{safe(data.get('project_description', ''))}",
        f"💰 {FIELD_LABELS_FA['proposed_budget']}: {safe(data.get('proposed_budget', ''))}",
        f"⏳ {FIELD_LABELS_FA['desired_timeline']}: {safe(data.get('desired_timeline', ''))}",
        f"📎 {FIELD_LABELS_FA['attachment']}: {'ارسال شد' if attachment else 'ندارد'}",
        "",
        "آیا اطلاعات بالا صحیح است؟",
    ]
    return "\n".join(lines)


def render_admin_notification(
    *,
    customer: Customer,
    estimation: Estimation | None,
    project_request: ProjectRequest,
    has_attachment: bool,
) -> str:
    lines = ["📥 <b>درخواست پروژه جدید</b>", ""]

    if estimation is not None:
        lines.append(f"🔧 خدمت: {estimation.service_type.label_fa}")
        lines.append(f"💰 برآورد قیمت: {estimation.price_range.format_fa()}")
        lines.append(f"⏳ برآورد زمان: {estimation.duration_range.format_fa()}")
        lines.append("")

    company_name = project_request.company_name
    company_name_display = safe(company_name) if company_name else "ندارد"
    lines.extend(
        [
            f"👤 {FIELD_LABELS_FA['full_name']}: {safe(project_request.full_name)}",
            f"📱 {FIELD_LABELS_FA['phone_number']}: {safe(project_request.phone_number)}",
            f"🏢 {FIELD_LABELS_FA['company_name']}: {company_name_display}",
            f"📝 {FIELD_LABELS_FA['project_description']}: "
            f"{safe(project_request.project_description)}",
            f"💰 {FIELD_LABELS_FA['proposed_budget']}: {safe(project_request.proposed_budget)}",
            f"⏳ {FIELD_LABELS_FA['desired_timeline']}: {safe(project_request.desired_timeline)}",
            f"📎 {FIELD_LABELS_FA['attachment']}: "
            f"{'دارد (پیام بعدی)' if has_attachment else 'ندارد'}",
            "",
            f"🆔 آیدی تلگرام مشتری: {customer.telegram_id}",
            f"📛 یوزرنیم: @{safe(customer.username)}" if customer.username else "📛 یوزرنیم: ندارد",
        ]
    )
    return "\n".join(lines)
