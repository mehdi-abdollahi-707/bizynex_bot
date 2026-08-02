"""Estimator copy must render the question progress and final result correctly."""

from apps.bot.content.estimator import DISCLAIMER_TEXT, render_question_text, render_result_text
from core.domain.estimator.calculator import EstimationResult
from core.domain.estimator.config import ESTIMATOR_CONFIGS
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType


def test_render_question_text_shows_progress() -> None:
    config = ESTIMATOR_CONFIGS[ServiceType.WORDPRESS_WEBSITE]
    text = render_question_text(config.questions[2], index=2, total=len(config.questions))
    assert text.startswith("(3/8)")
    assert config.questions[2].prompt_fa in text


def test_render_result_text_contains_price_duration_and_disclaimer() -> None:
    result = EstimationResult(
        price_range=PriceRange(45_000_000, 60_000_000),
        duration_range=DurationRange(35, 49),
        complexity_ratio=0.5,
    )
    text = render_result_text(result)

    assert "45 تا 60 میلیون تومان" in text
    assert "5 تا 7 هفته" in text
    assert DISCLAIMER_TEXT in text
    assert "💰" in text and "⏳" in text
