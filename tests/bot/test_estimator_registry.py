"""The estimator's entry points must be registered in the page system,
consistent with every other page's navigability guarantees.
"""

from apps.bot.keyboards.callback_data import EstimatorStartCallback
from apps.bot.pages.registry import PAGES
from core.domain.value_objects.service_type import ServiceType


def test_estimator_intro_page_is_registered_with_service_buttons() -> None:
    page = PAGES["estimator"]
    assert page.back_target == "main"
    assert page.extra_rows

    services = [
        EstimatorStartCallback.unpack(button.callback_data).service
        for row in page.extra_rows
        for button in row
    ]
    assert set(services) == {s.value for s in ServiceType}


def test_request_form_is_not_a_static_page() -> None:
    # Superseded in Phase 7 by a real FSM flow (apps.bot.handlers.request_form),
    # started via RequestFormStartCallback — it was never a real destination
    # the static nav registry should know about.
    assert "request_form" not in PAGES


def test_every_service_detail_page_has_a_start_estimate_button() -> None:
    from apps.bot.keyboards.services import service_detail_target

    for service_type in ServiceType:
        page = PAGES[service_detail_target(service_type)]
        all_buttons = [button for row in page.extra_rows for button in row]
        start_targets = [
            EstimatorStartCallback.unpack(b.callback_data).service
            for b in all_buttons
            if b.callback_data.startswith("est_start")
        ]
        assert service_type.value in start_targets
