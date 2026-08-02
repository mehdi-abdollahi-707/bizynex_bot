"""Structural sanity checks on every service's question set."""

import pytest

from core.domain.estimator.config import ESTIMATOR_CONFIGS
from core.domain.value_objects.service_type import ServiceType


def test_every_service_has_a_config() -> None:
    assert set(ESTIMATOR_CONFIGS.keys()) == set(ServiceType)


def test_every_service_has_at_least_one_question() -> None:
    for service_type, config in ESTIMATOR_CONFIGS.items():
        assert config.questions, service_type


def test_wordpress_questions_match_the_spec_example_exactly() -> None:
    config = ESTIMATOR_CONFIGS[ServiceType.WORDPRESS_WEBSITE]
    keys = [q.key for q in config.questions]
    assert keys == [
        "website_type",
        "payment_gateway",
        "languages",
        "admin_panel",
        "user_login",
        "blog",
        "seo_level",
        "sms_system",
    ]

    website_type = config.questions[0]
    assert [opt.label_fa for opt in website_type.options] == [
        "شرکتی",
        "فروشگاهی",
        "آموزشی",
        "شخصی",
        "خبری",
        "لندینگ پیج",
    ]


@pytest.mark.parametrize("service_type", list(ServiceType))
def test_question_keys_are_unique_within_a_service(service_type) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    keys = [q.key for q in config.questions]
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("service_type", list(ServiceType))
def test_duration_band_is_non_degenerate(service_type) -> None:
    band = ESTIMATOR_CONFIGS[service_type].duration_band
    assert band.min_days < band.max_days
