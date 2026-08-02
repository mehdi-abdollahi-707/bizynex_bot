"""DurationRange.format_fa() must match Bizynex's actual timeline copy exactly."""

import pytest

from core.domain.value_objects.duration_range import DurationRange


@pytest.mark.parametrize(
    ("min_days", "max_days", "expected"),
    [
        (28, 28, "حدود 4 هفته"),  # ~ WordPress site
        (180, 180, "حدود 6 ماه"),  # ~ Custom website
        (14, 14, "حدود 2 هفته"),  # ~ Telegram bot
        (3, 3, "حدود 3 روز"),  # ~ Poster
        (1, 1, "حدود 1 روز"),  # ~ Thumbnail
        (35, 49, "5 تا 7 هفته"),  # Estimator example, same unit
        (60, 90, "2 تا 3 ماه"),  # Range fully past the month threshold
        (3, 10, "3 روز تا 1 هفته"),  # Range straddling day -> week
    ],
)
def test_format_fa_matches_expected_output(min_days: int, max_days: int, expected: str) -> None:
    assert DurationRange(min_days, max_days).format_fa() == expected


def test_rejects_negative_bounds() -> None:
    with pytest.raises(ValueError, match="negative"):
        DurationRange(-1, 10)


def test_rejects_min_greater_than_max() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        DurationRange(20, 10)
