"""PriceRange.format_fa() must match Bizynex's actual pricing copy exactly."""

import pytest

from core.domain.value_objects.price_range import PriceRange


@pytest.mark.parametrize(
    ("min_toman", "max_toman", "expected"),
    [
        (25_000_000, 120_000_000, "25 تا 120 میلیون تومان"),  # WordPress site
        (80_000_000, 220_000_000, "80 تا 220 میلیون تومان"),  # Custom website
        (5_000_000, 30_000_000, "5 تا 30 میلیون تومان"),  # Telegram bot
        (3_000_000, 70_000_000, "3 تا 70 میلیون تومان"),  # n8n automation
        (300_000, 2_000_000, "300 هزار تا 2 میلیون تومان"),  # Poster (mixed units)
        (300_000, 1_000_000, "300 هزار تا 1 میلیون تومان"),  # Thumbnail (mixed units)
        (45_000_000, 60_000_000, "45 تا 60 میلیون تومان"),  # Estimator example
    ],
)
def test_format_fa_matches_spec_examples(min_toman: int, max_toman: int, expected: str) -> None:
    assert PriceRange(min_toman, max_toman).format_fa() == expected


def test_rejects_negative_bounds() -> None:
    with pytest.raises(ValueError, match="negative"):
        PriceRange(-1, 100)


def test_rejects_min_greater_than_max() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        PriceRange(200, 100)


def test_is_frozen() -> None:
    price_range = PriceRange(100, 200)
    with pytest.raises(AttributeError):
        price_range.min_toman = 50  # type: ignore[misc]
