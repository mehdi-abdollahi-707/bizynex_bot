"""Services list/comparison keyboards must expose every service exactly once."""

from apps.bot.keyboards.callback_data import NavCallback
from apps.bot.keyboards.services import (
    build_comparison_choice_rows,
    build_services_list_rows,
    build_website_service_extra_rows,
    service_detail_target,
)
from core.domain.value_objects.service_type import ServiceType


def _targets(rows) -> list[str]:
    return [NavCallback.unpack(button.callback_data).target for row in rows for button in row]


def test_services_list_has_one_button_per_service_plus_comparison() -> None:
    targets = _targets(build_services_list_rows())
    expected_service_targets = {service_detail_target(s) for s in ServiceType}

    assert expected_service_targets <= set(targets)
    assert "compare_websites" in targets
    assert len(targets) == len(ServiceType) + 1


def test_comparison_choice_offers_both_website_services() -> None:
    targets = _targets(build_comparison_choice_rows())
    assert set(targets) == {
        service_detail_target(ServiceType.WORDPRESS_WEBSITE),
        service_detail_target(ServiceType.CUSTOM_WEBSITE),
    }


def test_website_service_extra_row_links_to_comparison() -> None:
    targets = _targets(build_website_service_extra_rows())
    assert targets == ["compare_websites"]


def test_service_detail_target_has_no_colon() -> None:
    # aiogram's CallbackData uses ":" as its field separator internally —
    # a value containing one fails to pack.
    for service_type in ServiceType:
        assert ":" not in service_detail_target(service_type)
