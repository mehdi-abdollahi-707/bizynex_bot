"""Django ORM implementation of `EstimationRepository`."""

from __future__ import annotations

from apps.requests.models import Estimation as EstimationModel
from core.domain.entities.estimation import Estimation
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType


class DjangoEstimationRepository:
    async def create(self, estimation: Estimation) -> Estimation:
        model = await EstimationModel.objects.acreate(
            customer_id=estimation.customer_id,
            service_type=estimation.service_type.value,
            answers=estimation.answers,
            price_min_toman=estimation.price_range.min_toman,
            price_max_toman=estimation.price_range.max_toman,
            duration_min_days=estimation.duration_range.min_days,
            duration_max_days=estimation.duration_range.max_days,
        )
        return _to_entity(model)

    async def get_by_id(self, estimation_id: int) -> Estimation | None:
        try:
            model = await EstimationModel.objects.aget(id=estimation_id)
        except EstimationModel.DoesNotExist:
            return None
        return _to_entity(model)


def _to_entity(model: EstimationModel) -> Estimation:
    return Estimation(
        id=model.id,
        customer_id=model.customer_id,
        service_type=ServiceType(model.service_type),
        answers=model.answers,
        price_range=PriceRange(model.price_min_toman, model.price_max_toman),
        duration_range=DurationRange(model.duration_min_days, model.duration_max_days),
        created_at=model.created_at,
    )
