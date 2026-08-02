"""Estimation entity: a computed price/duration estimate for one service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType


@dataclass
class Estimation:
    customer_id: int
    service_type: ServiceType
    answers: dict[str, Any]
    price_range: PriceRange
    duration_range: DurationRange
    id: int | None = None
    created_at: datetime | None = None
