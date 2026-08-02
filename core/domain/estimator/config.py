"""Per-service estimator configuration: the question set and the duration
band each service's estimate is computed within.

The WordPress configurator (questions, order, and option text) is taken
verbatim from the spec's worked example. The other five services have no
spec-provided question set, so these are a reasoned first draft — grounded
in each service's catalog description/features (Phase 5) — meant to be
easy for Bizynex to tune: every number here is a `score` in [0.0, 1.0] or
a day count, none of it is scattered through handler code.

Price bounds are *not* configured here — they come from the shared
`core.domain.catalog.SERVICE_PRICE_RANGES`, the same numbers shown on each
service's catalog page, so an estimate can never quote outside what the
catalog already promised. Duration bounds are estimator-specific: catalog
duration text is a single "typical" figure, not a min/max band, so it
isn't reused as a clamp the way price is.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.estimator.question import AnswerOption, EstimatorQuestion
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.service_type import ServiceType


@dataclass(frozen=True)
class EstimatorConfig:
    service_type: ServiceType
    questions: tuple[EstimatorQuestion, ...]
    duration_band: DurationRange


def _opt(key: str, label_fa: str, score: float) -> AnswerOption:
    return AnswerOption(key=key, label_fa=label_fa, score=score)


_YES_NO = ("بله", "خیر")


def _yes_no_question(
    key: str, prompt_fa: str, *, yes_score: float, no_score: float = 0.0
) -> EstimatorQuestion:
    return EstimatorQuestion(
        key=key,
        prompt_fa=prompt_fa,
        options=(
            _opt("yes", _YES_NO[0], yes_score),
            _opt("no", _YES_NO[1], no_score),
        ),
    )


# ---------------------------------------------------------------------------
# 1) طراحی سایت وردپرسی — verbatim from the spec's worked example.
# ---------------------------------------------------------------------------
_WORDPRESS_QUESTIONS = (
    EstimatorQuestion(
        key="website_type",
        prompt_fa="نوع وب‌سایت:",
        options=(
            _opt("corporate", "شرکتی", 0.3),
            _opt("store", "فروشگاهی", 1.0),
            _opt("educational", "آموزشی", 0.5),
            _opt("personal", "شخصی", 0.1),
            _opt("news", "خبری", 0.6),
            _opt("landing", "لندینگ پیج", 0.0),
        ),
    ),
    _yes_no_question("payment_gateway", "آیا درگاه پرداخت نیاز دارید؟", yes_score=1.0),
    EstimatorQuestion(
        key="languages",
        prompt_fa="وب‌سایت چندزبانه باشد؟",
        options=(
            _opt("fa_only", "فقط فارسی", 0.0),
            _opt("fa_en", "فارسی و انگلیسی", 0.5),
            _opt("multilingual", "چندزبانه", 1.0),
        ),
    ),
    _yes_no_question("admin_panel", "آیا پنل مدیریت نیاز دارید؟", yes_score=1.0),
    _yes_no_question("user_login", "آیا سیستم ورود کاربران نیاز دارید؟", yes_score=0.7),
    _yes_no_question("blog", "آیا بخش وبلاگ نیاز دارید؟", yes_score=0.3),
    EstimatorQuestion(
        key="seo_level",
        prompt_fa="سطح سئو موردنظر:",
        options=(
            _opt("basic", "پایه", 0.0),
            _opt("professional", "حرفه‌ای", 0.5),
            _opt("advanced", "پیشرفته", 1.0),
        ),
    ),
    _yes_no_question("sms_system", "آیا سیستم پیامکی نیاز دارید؟", yes_score=0.6),
)

# ---------------------------------------------------------------------------
# 2) طراحی سایت اختصاصی — mirrors the catalog's advertised features
#    (REST API, احراز هویت, پنل مدیریت, ...).
# ---------------------------------------------------------------------------
_CUSTOM_WEBSITE_QUESTIONS = (
    EstimatorQuestion(
        key="project_type",
        prompt_fa="نوع پروژه:",
        options=(
            _opt("internal_panel", "پنل مدیریتی داخلی", 0.2),
            _opt("b2c_platform", "پلتفرم مشتری‌محور (B2C)", 0.45),
            _opt("online_store", "فروشگاه اینترنتی اختصاصی", 0.65),
            _opt("marketplace", "سیستم پیچیده (مارکت‌پلیس یا شبکه اجتماعی)", 1.0),
        ),
    ),
    _yes_no_question(
        "auth_roles",
        "آیا نیاز به احراز هویت و سطوح دسترسی کاربران دارید؟",
        yes_score=0.7,
        no_score=0.1,
    ),
    _yes_no_question(
        "external_apis",
        "آیا اتصال به سرویس‌ها یا API‌های خارجی نیاز است؟",
        yes_score=0.7,
        no_score=0.1,
    ),
    _yes_no_question(
        "admin_panel", "آیا نیاز به پنل مدیریت اختصاصی دارید؟", yes_score=0.6, no_score=0.1
    ),
    _yes_no_question("online_payment", "آیا قابلیت پرداخت آنلاین نیاز دارید؟", yes_score=0.8),
    EstimatorQuestion(
        key="ui_level",
        prompt_fa="سطح طراحی رابط کاربری (UI/UX) موردنظر:",
        options=(
            _opt("standard", "ساده و استاندارد", 0.2),
            _opt("professional", "حرفه‌ای و سفارشی", 0.6),
            _opt("bespoke", "کاملاً اختصاصی با طراحی گرافیکی ویژه", 1.0),
        ),
    ),
)

# ---------------------------------------------------------------------------
# 3) ساخت ربات تلگرام
# ---------------------------------------------------------------------------
_TELEGRAM_BOT_QUESTIONS = (
    EstimatorQuestion(
        key="bot_type",
        prompt_fa="نوع ربات موردنظر:",
        options=(
            _opt("info_support", "ربات اطلاع‌رسانی یا پشتیبانی ساده", 0.15),
            _opt("sales", "ربات فروش و سفارش‌گیری", 0.5),
            _opt("admin_panel", "ربات با پنل مدیریت و گزارش‌گیری", 0.75),
            _opt("advanced", "ربات هوشمند با قابلیت‌های سفارشی پیشرفته", 1.0),
        ),
    ),
    _yes_no_question("payment_gateway", "آیا اتصال به درگاه پرداخت نیاز دارید؟", yes_score=0.7),
    _yes_no_question("web_panel", "آیا نیاز به پنل مدیریت وب دارید؟", yes_score=0.6),
    _yes_no_question(
        "external_integration",
        "آیا اتصال به دیتابیس یا سیستم‌های خارجی (CRM، فروشگاه و ...) نیاز است؟",
        yes_score=0.6,
    ),
    _yes_no_question(
        "scheduled_messages",
        "آیا نیاز به اتوماسیون یا ارسال پیام‌های زمان‌بندی‌شده دارید؟",
        yes_score=0.4,
    ),
)

# ---------------------------------------------------------------------------
# 4) اتوماسیون با n8n
# ---------------------------------------------------------------------------
_N8N_AUTOMATION_QUESTIONS = (
    EstimatorQuestion(
        key="service_count",
        prompt_fa="تعداد سرویس‌هایی که باید به هم متصل شوند:",
        options=(
            _opt("two", "2 سرویس", 0.15),
            _opt("three_four", "3 تا 4 سرویس", 0.45),
            _opt("five_plus", "5 سرویس یا بیشتر", 0.85),
        ),
    ),
    _yes_no_question(
        "conditional_logic",
        "آیا نیاز به منطق شرطی یا پردازش پیچیده داده دارید؟",
        yes_score=0.7,
        no_score=0.1,
    ),
    _yes_no_question(
        "undocumented_api",
        "آیا اتصال به API اختصاصی یا سرویس بدون مستندات آماده نیاز است؟",
        yes_score=0.8,
        no_score=0.1,
    ),
    EstimatorQuestion(
        key="execution_volume",
        prompt_fa="میزان تکرار و حجم اجرای فرآیند:",
        options=(
            _opt("low", "کم (چندبار در روز)", 0.2),
            _opt("medium", "متوسط (هر ساعت)", 0.5),
            _opt("high", "بالا (لحظه‌ای یا حجم زیاد)", 0.9),
        ),
    ),
)

# ---------------------------------------------------------------------------
# 5) طراحی پوستر
# ---------------------------------------------------------------------------
_POSTER_DESIGN_QUESTIONS = (
    EstimatorQuestion(
        key="poster_count",
        prompt_fa="تعداد پوستر موردنیاز:",
        options=(
            _opt("one", "یک پوستر", 0.1),
            _opt("two_three", "2 تا 3 پوستر", 0.4),
            _opt("more", "بیش از 3 پوستر (مجموعه)", 0.8),
        ),
    ),
    EstimatorQuestion(
        key="usage",
        prompt_fa="نوع استفاده:",
        options=(
            _opt("digital_only", "فقط فضای مجازی", 0.2),
            _opt("print_only", "چاپی", 0.6),
            _opt("both", "فضای مجازی و چاپی", 0.8),
        ),
    ),
    _yes_no_question(
        "custom_concept",
        "آیا نیاز به مفهوم‌پردازی و ایده‌سازی خاص دارید؟",
        yes_score=0.7,
        no_score=0.2,
    ),
)

# ---------------------------------------------------------------------------
# 6) طراحی تامنیل یوتیوب و کاور اینستاگرام
# ---------------------------------------------------------------------------
_THUMBNAIL_COVER_QUESTIONS = (
    EstimatorQuestion(
        key="design_type",
        prompt_fa="نوع طراحی موردنیاز:",
        options=(
            _opt("thumbnail_only", "فقط تامنیل یوتیوب", 0.3),
            _opt("cover_only", "فقط کاور اینستاگرام", 0.3),
            _opt("both", "هر دو", 0.6),
        ),
    ),
    EstimatorQuestion(
        key="design_count",
        prompt_fa="تعداد طرح موردنیاز:",
        options=(
            _opt("one", "یک طرح", 0.1),
            _opt("template_variants", "یک قالب با چند نسخه تکرارشونده", 0.5),
            _opt("many_distinct", "چند طرح متفاوت", 0.9),
        ),
    ),
)


ESTIMATOR_CONFIGS: dict[ServiceType, EstimatorConfig] = {
    ServiceType.WORDPRESS_WEBSITE: EstimatorConfig(
        service_type=ServiceType.WORDPRESS_WEBSITE,
        questions=_WORDPRESS_QUESTIONS,
        duration_band=DurationRange(21, 49),
    ),
    ServiceType.CUSTOM_WEBSITE: EstimatorConfig(
        service_type=ServiceType.CUSTOM_WEBSITE,
        questions=_CUSTOM_WEBSITE_QUESTIONS,
        duration_band=DurationRange(90, 240),
    ),
    ServiceType.TELEGRAM_BOT: EstimatorConfig(
        service_type=ServiceType.TELEGRAM_BOT,
        questions=_TELEGRAM_BOT_QUESTIONS,
        duration_band=DurationRange(7, 30),
    ),
    ServiceType.N8N_AUTOMATION: EstimatorConfig(
        service_type=ServiceType.N8N_AUTOMATION,
        questions=_N8N_AUTOMATION_QUESTIONS,
        duration_band=DurationRange(10, 45),
    ),
    ServiceType.POSTER_DESIGN: EstimatorConfig(
        service_type=ServiceType.POSTER_DESIGN,
        questions=_POSTER_DESIGN_QUESTIONS,
        duration_band=DurationRange(1, 6),
    ),
    ServiceType.THUMBNAIL_COVER_DESIGN: EstimatorConfig(
        service_type=ServiceType.THUMBNAIL_COVER_DESIGN,
        questions=_THUMBNAIL_COVER_QUESTIONS,
        duration_band=DurationRange(1, 3),
    ),
}
