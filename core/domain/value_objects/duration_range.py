"""DurationRange: an estimated timeline in days, with Persian formatting.

Renders as "حدود N {unit}" when min == max (a single approximate figure),
or "X تا Y {unit(s)}" for a true range — same unit when both bounds land
in it ("5 تا 7 هفته"), mixed units when they straddle the day/week/month
boundary.

This formatter is for *dynamically computed* durations, i.e. the project
estimator's output (Phase 6). The six service catalog pages (Phase 5) show
fixed marketing copy per service ("حدود 4 هفته", "2 هفته تا 1 ماه", ...)
authored as literal Persian strings — that copy doesn't need to round-trip
through this value object, so it isn't constrained by its unit thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass

_DAYS_PER_WEEK = 7
_DAYS_PER_MONTH = 30
# Below this, express the range in weeks even though it technically exceeds
# one month (30 days) — "7 هفته" reads more naturally than "2 ماه" for ~7
# weeks. Only longer estimates switch to months.
_MONTH_THRESHOLD_DAYS = 60


@dataclass(frozen=True)
class DurationRange:
    min_days: int
    max_days: int

    def __post_init__(self) -> None:
        if self.min_days < 0 or self.max_days < 0:
            raise ValueError("Duration bounds cannot be negative.")
        if self.min_days > self.max_days:
            raise ValueError("min_days cannot exceed max_days.")

    def format_fa(self) -> str:
        if self.min_days == self.max_days:
            value, unit = _split_duration(self.min_days)
            return f"حدود {value} {unit}"

        min_value, min_unit = _split_duration(self.min_days)
        max_value, max_unit = _split_duration(self.max_days)

        if min_unit == max_unit:
            return f"{min_value} تا {max_value} {min_unit}"
        return f"{min_value} {min_unit} تا {max_value} {max_unit}"


def _split_duration(days: int) -> tuple[int, str]:
    if days >= _MONTH_THRESHOLD_DAYS:
        return round(days / _DAYS_PER_MONTH), "ماه"
    if days >= _DAYS_PER_WEEK:
        return round(days / _DAYS_PER_WEEK), "هفته"
    return days, "روز"
