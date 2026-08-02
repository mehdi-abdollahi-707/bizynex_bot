"""Repository interface for Estimation persistence."""

from __future__ import annotations

from typing import Protocol

from core.domain.entities.estimation import Estimation


class EstimationRepository(Protocol):
    async def create(self, estimation: Estimation) -> Estimation: ...

    async def get_by_id(self, estimation_id: int) -> Estimation | None: ...
