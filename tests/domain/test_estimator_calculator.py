"""The pricing engine must always return a valid, in-bounds, non-degenerate
range — for every service and across the full spectrum of answers.
"""

import pytest

from core.domain.catalog import SERVICE_PRICE_RANGES
from core.domain.estimator.calculator import calculate_estimate
from core.domain.estimator.config import ESTIMATOR_CONFIGS
from core.domain.value_objects.service_type import ServiceType


def _cheapest_answers(config) -> dict[str, str]:
    return {q.key: min(q.options, key=lambda o: o.score).key for q in config.questions}


def _priciest_answers(config) -> dict[str, str]:
    return {q.key: max(q.options, key=lambda o: o.score).key for q in config.questions}


def _mixed_answers(config) -> dict[str, str]:
    # Alternate cheapest/priciest per question — a "middling" combination.
    answers = {}
    for i, q in enumerate(config.questions):
        chosen = (
            min(q.options, key=lambda o: o.score)
            if i % 2 == 0
            else max(q.options, key=lambda o: o.score)
        )
        answers[q.key] = chosen.key
    return answers


@pytest.mark.parametrize("service_type", list(ServiceType))
def test_cheapest_answers_land_near_the_low_end(service_type) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    result = calculate_estimate(config, _cheapest_answers(config))
    band = SERVICE_PRICE_RANGES[service_type]

    assert band.min_toman <= result.price_range.min_toman
    assert result.price_range.max_toman <= band.max_toman
    # Cheapest combo should sit in the lower half of the band.
    midpoint = (band.min_toman + band.max_toman) / 2
    assert result.price_range.max_toman <= midpoint


@pytest.mark.parametrize("service_type", list(ServiceType))
def test_priciest_answers_land_near_the_high_end(service_type) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    result = calculate_estimate(config, _priciest_answers(config))
    band = SERVICE_PRICE_RANGES[service_type]

    assert band.min_toman <= result.price_range.min_toman
    assert result.price_range.max_toman <= band.max_toman
    midpoint = (band.min_toman + band.max_toman) / 2
    assert result.price_range.min_toman >= midpoint


@pytest.mark.parametrize("service_type", list(ServiceType))
def test_priciest_beats_cheapest(service_type) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    cheap = calculate_estimate(config, _cheapest_answers(config))
    pricey = calculate_estimate(config, _priciest_answers(config))

    assert cheap.price_range.max_toman <= pricey.price_range.min_toman
    assert cheap.duration_range.max_days <= pricey.duration_range.max_days


@pytest.mark.parametrize("service_type", list(ServiceType))
@pytest.mark.parametrize("answer_fn", [_cheapest_answers, _priciest_answers, _mixed_answers])
def test_result_is_always_within_bounds_and_non_degenerate(service_type, answer_fn) -> None:
    config = ESTIMATOR_CONFIGS[service_type]
    result = calculate_estimate(config, answer_fn(config))
    price_band = SERVICE_PRICE_RANGES[service_type]
    duration_band = config.duration_band

    assert price_band.min_toman <= result.price_range.min_toman
    assert result.price_range.max_toman <= price_band.max_toman
    assert result.price_range.min_toman < result.price_range.max_toman

    assert duration_band.min_days <= result.duration_range.min_days
    assert result.duration_range.max_days <= duration_band.max_days
    assert result.duration_range.min_days < result.duration_range.max_days

    assert 0.0 <= result.complexity_ratio <= 1.0


def test_missing_answer_raises_key_error() -> None:
    config = ESTIMATOR_CONFIGS[ServiceType.POSTER_DESIGN]
    incomplete_answers = {config.questions[0].key: config.questions[0].options[0].key}

    with pytest.raises(KeyError):
        calculate_estimate(config, incomplete_answers)


def test_invalid_option_key_raises_key_error() -> None:
    config = ESTIMATOR_CONFIGS[ServiceType.POSTER_DESIGN]
    answers = {q.key: q.options[0].key for q in config.questions}
    answers[config.questions[0].key] = "not-a-real-option"

    with pytest.raises(KeyError):
        calculate_estimate(config, answers)
