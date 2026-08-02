"""Turns a customer's configurator answers into a price/duration estimate.

Never returns a fixed number — always a range. Each answered question
contributes a `score` in [0.0, 1.0]; their average is the project's
"complexity ratio", which places a window within the service's price band
(`core.domain.catalog.SERVICE_PRICE_RANGES`) and duration band
(`EstimatorConfig.duration_band`). The window's width is a fixed fraction
of the band — self-scaling, so it stays sane for both a 700k-Toman band
(thumbnails) and a 140M-Toman one (custom websites) — and if step-rounding
ever collapses it to a single figure, it's nudged apart by one step rather
than clamped to a fixed number, reflecting that this is a preliminary
estimate, not a final quote.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.catalog import SERVICE_PRICE_RANGES
from core.domain.estimator.config import EstimatorConfig
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange

# The returned range spans this fraction of the service's full band.
_RANGE_WIDTH_FRACTION = 0.16

_PRICE_STEP_TOMAN = 100_000


@dataclass(frozen=True)
class EstimationResult:
    price_range: PriceRange
    duration_range: DurationRange
    complexity_ratio: float


def calculate_estimate(config: EstimatorConfig, answers: dict[str, str]) -> EstimationResult:
    """`answers` maps question key -> chosen option key, one per question in `config.questions`."""
    ratio = _complexity_ratio(config, answers)

    price_band = SERVICE_PRICE_RANGES[config.service_type]
    price_low, price_high = _scaled_window(
        band_min=price_band.min_toman, band_max=price_band.max_toman, ratio=ratio
    )
    price_low = _round_to_step(price_low, step=_PRICE_STEP_TOMAN)
    price_high = _round_to_step(price_high, step=_PRICE_STEP_TOMAN)
    if price_high <= price_low:
        price_high = min(price_low + _PRICE_STEP_TOMAN, price_band.max_toman)
    price_low = min(price_low, price_high)

    duration_low, duration_high = _scaled_window(
        band_min=config.duration_band.min_days,
        band_max=config.duration_band.max_days,
        ratio=ratio,
    )
    duration_low = round(duration_low)
    duration_high = round(duration_high)
    if duration_high <= duration_low:
        duration_high = min(duration_low + 1, config.duration_band.max_days)
    duration_low = min(duration_low, duration_high)

    return EstimationResult(
        price_range=PriceRange(int(price_low), int(price_high)),
        duration_range=DurationRange(int(duration_low), int(duration_high)),
        complexity_ratio=ratio,
    )


def _complexity_ratio(config: EstimatorConfig, answers: dict[str, str]) -> float:
    scores = [question.option_by_key(answers[question.key]).score for question in config.questions]
    return sum(scores) / len(scores) if scores else 0.0


def _scaled_window(*, band_min: float, band_max: float, ratio: float) -> tuple[float, float]:
    """Place a `_RANGE_WIDTH_FRACTION`-wide window inside [band_min, band_max],
    centered on the point `ratio` maps to, shifted inward if it would overflow.
    """
    total = band_max - band_min
    center = band_min + ratio * total
    half_width = (_RANGE_WIDTH_FRACTION * total) / 2

    low = center - half_width
    high = center + half_width

    if low < band_min:
        high += band_min - low
        low = band_min
    if high > band_max:
        low -= high - band_max
        high = band_max

    return max(low, band_min), min(high, band_max)


def _round_to_step(value: float, *, step: int) -> float:
    return round(value / step) * step
