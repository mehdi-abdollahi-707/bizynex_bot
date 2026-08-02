"""PriceRange: an estimated cost range in Iranian Tomans, with Persian formatting.

Estimates are always ranges, never a fixed number — `format_fa()` renders
them the way Bizynex actually writes prices for customers, e.g.
"25 تا 120 میلیون تومان" (shared unit) or "300 هزار تا 2 میلیون تومان"
(mixed units).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceRange:
    min_toman: int
    max_toman: int

    def __post_init__(self) -> None:
        if self.min_toman < 0 or self.max_toman < 0:
            raise ValueError("Price bounds cannot be negative.")
        if self.min_toman > self.max_toman:
            raise ValueError("min_toman cannot exceed max_toman.")

    def format_fa(self) -> str:
        min_text, min_unit = _split_amount(self.min_toman)
        max_text, max_unit = _split_amount(self.max_toman)

        if min_unit == max_unit:
            unit_suffix = f" {min_unit}" if min_unit else ""
            return f"{min_text} تا {max_text}{unit_suffix} تومان"

        min_part = f"{min_text} {min_unit}" if min_unit else min_text
        max_part = f"{max_text} {max_unit}" if max_unit else max_text
        return f"{min_part} تا {max_part} تومان"


def _split_amount(amount: int) -> tuple[str, str | None]:
    if amount >= 1_000_000_000:
        return _trim(amount / 1_000_000_000), "میلیارد"
    if amount >= 1_000_000:
        return _trim(amount / 1_000_000), "میلیون"
    if amount >= 1_000:
        return _trim(amount / 1_000), "هزار"
    return str(amount), None


def _trim(value: float) -> str:
    """Format with one decimal place, dropping a trailing '.0'."""
    return f"{value:.1f}".rstrip("0").rstrip(".")
