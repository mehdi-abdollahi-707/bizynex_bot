"""Persian copy for the services catalog: the list page, each service's
detail page, and the WordPress-vs-custom comparison page.

Prices come from `core.domain.catalog.SERVICE_PRICE_RANGES` — the shared
canonical bounds also read by the Phase 6 estimator's pricing calculation,
so a displayed price and a computed estimate can never drift apart. Their
`.format_fa()` (domain layer, unit-tested against every figure below) keeps
catalog copy and estimator output formatted identically. Durations here are
literal strings — see `DurationRange`'s docstring for why marketing copy
isn't forced through that formatter's unit thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.catalog import SERVICE_PRICE_RANGES
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType


@dataclass(frozen=True)
class ServiceCatalogEntry:
    service_type: ServiceType
    number_emoji: str
    description: str
    price_range: PriceRange
    duration_text: str
    features: list[str] | None = None
    frontend: str | None = None
    backend: str | None = None


SERVICE_CATALOG: dict[ServiceType, ServiceCatalogEntry] = {
    ServiceType.WORDPRESS_WEBSITE: ServiceCatalogEntry(
        service_type=ServiceType.WORDPRESS_WEBSITE,
        number_emoji="1️⃣",
        description=("طراحی انواع سایت شرکتی، فروشگاهی، آموزشی، شخصی و خبری با WordPress."),
        features=[
            "طراحی واکنش‌گرا",
            "پنل مدیریت",
            "سئو پایه",
            "امنیت مناسب",
            "قابلیت توسعه",
        ],
        price_range=SERVICE_PRICE_RANGES[ServiceType.WORDPRESS_WEBSITE],
        duration_text="حدود 4 هفته",
    ),
    ServiceType.CUSTOM_WEBSITE: ServiceCatalogEntry(
        service_type=ServiceType.CUSTOM_WEBSITE,
        number_emoji="2️⃣",
        description=("طراحی و توسعه وب‌اپلیکیشن اختصاصی با معماری حرفه‌ای و قابلیت توسعه بالا."),
        frontend="React",
        backend="Django",
        features=[
            "رابط کاربری اختصاصی",
            "REST API",
            "احراز هویت",
            "پنل مدیریت",
            "امنیت بالا",
            "توسعه‌پذیری",
        ],
        price_range=SERVICE_PRICE_RANGES[ServiceType.CUSTOM_WEBSITE],
        duration_text="حدود 6 ماه",
    ),
    ServiceType.TELEGRAM_BOT: ServiceCatalogEntry(
        service_type=ServiceType.TELEGRAM_BOT,
        number_emoji="3️⃣",
        description=(
            "طراحی ربات‌های حرفه‌ای تلگرام با امکانات سفارشی، اتصال به API، درگاه "
            "پرداخت و اتوماسیون."
        ),
        price_range=SERVICE_PRICE_RANGES[ServiceType.TELEGRAM_BOT],
        duration_text="حدود 2 هفته",
    ),
    ServiceType.N8N_AUTOMATION: ServiceCatalogEntry(
        service_type=ServiceType.N8N_AUTOMATION,
        number_emoji="4️⃣",
        description=("اتوماسیون فرآیندهای کسب‌وکار، اتصال سرویس‌ها، CRM، API و حذف کارهای تکراری."),
        price_range=SERVICE_PRICE_RANGES[ServiceType.N8N_AUTOMATION],
        duration_text="2 هفته تا 1 ماه",
    ),
    ServiceType.POSTER_DESIGN: ServiceCatalogEntry(
        service_type=ServiceType.POSTER_DESIGN,
        number_emoji="5️⃣",
        description="طراحی پوستر تبلیغاتی حرفه‌ای برای شبکه‌های اجتماعی و چاپ.",
        price_range=SERVICE_PRICE_RANGES[ServiceType.POSTER_DESIGN],
        duration_text="حدود 3 روز",
    ),
    ServiceType.THUMBNAIL_COVER_DESIGN: ServiceCatalogEntry(
        service_type=ServiceType.THUMBNAIL_COVER_DESIGN,
        number_emoji="6️⃣",
        description=(
            "طراحی تامنیل حرفه‌ای و کاور اینستاگرام با تمرکز بر افزایش نرخ کلیک و " "زیبایی بصری."
        ),
        price_range=SERVICE_PRICE_RANGES[ServiceType.THUMBNAIL_COVER_DESIGN],
        duration_text="حدود 1 روز",
    ),
}


def render_services_list_text() -> str:
    return (
        "💼 <b>خدمات ما</b>\n\n"
        "Bizynex مجموعه‌ای از خدمات دیجیتال را برای رشد کسب‌وکار شما ارائه می‌دهد.\n\n"
        "برای مشاهده جزئیات هر خدمت، از دکمه‌های زیر استفاده کنید 👇"
    )


def render_service_page(entry: ServiceCatalogEntry) -> str:
    lines = [f"{entry.number_emoji} <b>{entry.service_type.label_fa}</b>", ""]

    stack_parts = []
    if entry.frontend:
        stack_parts.append(f"Frontend: {entry.frontend}")
    if entry.backend:
        stack_parts.append(f"Backend: {entry.backend}")
    if stack_parts:
        lines.append(" | ".join(stack_parts))
        lines.append("")

    lines.append(entry.description)
    lines.append("")

    if entry.features:
        lines.append("<b>ویژگی‌ها:</b>")
        lines.extend(f"• {feature}" for feature in entry.features)
        lines.append("")

    lines.append(f"💰 <b>قیمت:</b> {entry.price_range.format_fa()}")
    lines.append(f"⏳ <b>زمان اجرا:</b> {entry.duration_text}")

    return "\n".join(lines)


def render_comparison_text() -> str:
    wordpress = SERVICE_CATALOG[ServiceType.WORDPRESS_WEBSITE]
    custom = SERVICE_CATALOG[ServiceType.CUSTOM_WEBSITE]

    return (
        "🆚 <b>مقایسه: وردپرسی در برابر اختصاصی</b>\n\n"
        "برای انتخاب مناسب‌ترین راهکار، این دو گزینه را از چند جنبه با هم مقایسه "
        "می‌کنیم:\n\n"
        "<b>💰 هزینه</b>\n"
        f"وردپرسی: {wordpress.price_range.format_fa()}\n"
        f"اختصاصی: {custom.price_range.format_fa()}\n\n"
        "<b>⏳ زمان اجرا</b>\n"
        f"وردپرسی: {wordpress.duration_text}\n"
        f"اختصاصی: {custom.duration_text}\n\n"
        "<b>📈 توسعه‌پذیری</b>\n"
        "وردپرسی: مناسب برای نیازهای رایج، با افزونه‌ها قابل گسترش\n"
        "اختصاصی: کاملاً نامحدود؛ معماری بر اساس نیاز شما طراحی می‌شود\n\n"
        "<b>🔒 امنیت</b>\n"
        "وردپرسی: نیازمند بروزرسانی و مدیریت منظم\n"
        "اختصاصی: امنیت بالاتر به دلیل کد اختصاصی و سطح حمله کمتر\n\n"
        "<b>⚡ سرعت</b>\n"
        "وردپرسی: وابسته به تعداد افزونه‌ها و کیفیت هاست\n"
        "اختصاصی: بهینه‌سازی‌شده برای عملکرد و سرعت بالا\n\n"
        "<b>🎨 قابلیت سفارشی‌سازی</b>\n"
        "وردپرسی: در چارچوب امکانات قالب و افزونه\n"
        "اختصاصی: کاملاً مطابق با طراحی و نیاز شما\n\n"
        "<b>🏢 مناسب برای چه کسب‌وکارهایی؟</b>\n"
        "وردپرسی: کسب‌وکارهای کوچک و متوسط با بودجه و زمان محدود\n"
        "اختصاصی: کسب‌وکارهایی با نیازهای پیچیده و برنامه رشد بلندمدت\n\n"
        "برای مشاهده جزئیات کامل هر گزینه، یکی را انتخاب کنید 👇"
    )
