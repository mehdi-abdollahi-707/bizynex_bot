"""The services catalog must cover all 6 services with spec-accurate copy,
and every service/comparison page must be reachable through the registry.
"""

from apps.bot.content.services import (
    SERVICE_CATALOG,
    render_comparison_text,
    render_service_page,
    render_services_list_text,
)
from apps.bot.keyboards.services import service_detail_target
from apps.bot.pages.registry import PAGES
from core.domain.value_objects.service_type import ServiceType


def test_catalog_has_all_six_services() -> None:
    assert set(SERVICE_CATALOG.keys()) == set(ServiceType)


def test_every_catalog_entry_matches_its_own_service_type() -> None:
    for service_type, entry in SERVICE_CATALOG.items():
        assert entry.service_type == service_type


def test_only_wordpress_and_custom_have_feature_lists() -> None:
    for service_type, entry in SERVICE_CATALOG.items():
        if service_type in (ServiceType.WORDPRESS_WEBSITE, ServiceType.CUSTOM_WEBSITE):
            assert entry.features
        else:
            assert entry.features is None


def test_custom_website_has_a_tech_stack() -> None:
    entry = SERVICE_CATALOG[ServiceType.CUSTOM_WEBSITE]
    assert entry.frontend == "React"
    assert entry.backend == "Django"


def test_service_page_includes_price_and_duration() -> None:
    entry = SERVICE_CATALOG[ServiceType.TELEGRAM_BOT]
    text = render_service_page(entry)
    assert entry.price_range.format_fa() in text
    assert entry.duration_text in text
    assert entry.description in text


def test_every_service_is_registered_as_a_navigable_page() -> None:
    for service_type in ServiceType:
        target = service_detail_target(service_type)
        assert target in PAGES
        assert PAGES[target].back_target == "services"


def test_services_list_page_is_registered_and_non_empty() -> None:
    assert PAGES["services"].text == render_services_list_text()
    assert PAGES["services"].extra_rows


def test_comparison_page_is_registered_with_choice_buttons() -> None:
    page = PAGES["compare_websites"]
    assert page.text == render_comparison_text()
    assert page.back_target == "services"
    assert page.extra_rows


def test_comparison_text_covers_every_required_dimension() -> None:
    text = render_comparison_text()
    for dimension in ["هزینه", "زمان اجرا", "توسعه‌پذیری", "امنیت", "سرعت", "قابلیت سفارشی‌سازی"]:
        assert dimension in text
