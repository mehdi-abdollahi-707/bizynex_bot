"""Static page registry: page id -> its text, "بازگشت" target, and any
extra buttons shown above the standard nav row.

Adding a new static page is one entry here, no handler changes. Pages
belonging to a real multi-step flow (the estimator's and the request
form's own question pages) aren't here at all — they're driven by their
own FSM flows (`apps.bot.handlers.estimator`, `apps.bot.handlers.request_form`)
instead, since the generic nav system can't drive branching, stateful
conversations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aiogram.types import InlineKeyboardButton

from apps.bot.content import about, contact, faq, portfolio
from apps.bot.content.estimator import ESTIMATOR_INTRO_TEXT
from apps.bot.content.services import (
    SERVICE_CATALOG,
    render_comparison_text,
    render_service_page,
    render_services_list_text,
)
from apps.bot.keyboards.estimator import build_estimator_intro_rows, build_start_estimate_row
from apps.bot.keyboards.services import (
    build_comparison_choice_rows,
    build_services_list_rows,
    build_website_service_extra_rows,
    service_detail_target,
)
from core.domain.value_objects.service_type import ServiceType


@dataclass(frozen=True)
class Page:
    text: str
    back_target: str = "main"
    extra_rows: list[list[InlineKeyboardButton]] = field(default_factory=list)


PAGES: dict[str, Page] = {
    "about": Page(text=about.ABOUT_TEXT),
    "contact": Page(text=contact.CONTACT_TEXT),
    "faq": Page(text=faq.FAQ_TEXT),
    "portfolio": Page(text=portfolio.PORTFOLIO_TEXT),
    "services": Page(
        text=render_services_list_text(),
        back_target="main",
        extra_rows=build_services_list_rows(),
    ),
    "compare_websites": Page(
        text=render_comparison_text(),
        back_target="services",
        extra_rows=build_comparison_choice_rows(),
    ),
    "estimator": Page(
        text=ESTIMATOR_INTRO_TEXT,
        back_target="main",
        extra_rows=build_estimator_intro_rows(),
    ),
}

_WEBSITE_COMPARISON_TARGETS = {ServiceType.WORDPRESS_WEBSITE, ServiceType.CUSTOM_WEBSITE}

for _service_type, _entry in SERVICE_CATALOG.items():
    _extra_rows = [build_start_estimate_row(_service_type)]
    if _service_type in _WEBSITE_COMPARISON_TARGETS:
        _extra_rows += build_website_service_extra_rows()

    PAGES[service_detail_target(_service_type)] = Page(
        text=render_service_page(_entry),
        back_target="services",
        extra_rows=_extra_rows,
    )
