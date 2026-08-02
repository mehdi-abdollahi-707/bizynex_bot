"""Canonical per-service price ranges.

Single source of truth read by both the services catalog (Phase 5,
presentation) and the estimator's pricing calculation (Phase 6, business
logic) — so a price shown on a service page and a price the estimator
computes for that same service can never drift apart. The estimator always
clamps its output within these bounds: whatever the catalog page already
told the customer is possible, the estimator can narrow but never exceed.
"""

from __future__ import annotations

from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType

SERVICE_PRICE_RANGES: dict[ServiceType, PriceRange] = {
    ServiceType.WORDPRESS_WEBSITE: PriceRange(25_000_000, 120_000_000),
    ServiceType.CUSTOM_WEBSITE: PriceRange(80_000_000, 220_000_000),
    ServiceType.TELEGRAM_BOT: PriceRange(5_000_000, 30_000_000),
    ServiceType.N8N_AUTOMATION: PriceRange(3_000_000, 70_000_000),
    ServiceType.POSTER_DESIGN: PriceRange(300_000, 2_000_000),
    ServiceType.THUMBNAIL_COVER_DESIGN: PriceRange(300_000, 1_000_000),
}
