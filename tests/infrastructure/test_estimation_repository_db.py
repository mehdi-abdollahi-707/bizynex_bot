"""DB-backed round-trip tests for DjangoEstimationRepository.

Requires a live PostgreSQL connection — see test_customer_repository_db.py.
"""

import pytest

from core.domain.entities.customer import Customer
from core.domain.entities.estimation import Estimation
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType
from core.infrastructure.repositories.django_customer_repository import (
    DjangoCustomerRepository,
)
from core.infrastructure.repositories.django_estimation_repository import (
    DjangoEstimationRepository,
)

pytestmark = pytest.mark.django_db(transaction=True)


async def _make_customer() -> Customer:
    return await DjangoCustomerRepository().upsert(
        telegram_id=555, first_name="علی", last_name=None, username=None
    )


async def test_create_persists_and_round_trips_every_field() -> None:
    customer = await _make_customer()
    repository = DjangoEstimationRepository()

    estimation = Estimation(
        customer_id=customer.id,
        service_type=ServiceType.WORDPRESS_WEBSITE,
        answers={"website_type": "store", "payment_gateway": "yes"},
        price_range=PriceRange(45_000_000, 60_000_000),
        duration_range=DurationRange(35, 49),
    )

    created = await repository.create(estimation)

    assert created.id is not None
    assert created.customer_id == customer.id
    assert created.service_type == ServiceType.WORDPRESS_WEBSITE
    assert created.answers == {"website_type": "store", "payment_gateway": "yes"}
    assert created.price_range == PriceRange(45_000_000, 60_000_000)
    assert created.duration_range == DurationRange(35, 49)
    assert created.created_at is not None


async def test_get_by_id_returns_none_when_missing() -> None:
    repository = DjangoEstimationRepository()
    assert await repository.get_by_id(999999) is None


async def test_get_by_id_finds_an_existing_estimation() -> None:
    customer = await _make_customer()
    repository = DjangoEstimationRepository()
    created = await repository.create(
        Estimation(
            customer_id=customer.id,
            service_type=ServiceType.POSTER_DESIGN,
            answers={},
            price_range=PriceRange(300_000, 600_000),
            duration_range=DurationRange(2, 4),
        )
    )

    found = await repository.get_by_id(created.id)

    assert found is not None
    assert found.service_type == ServiceType.POSTER_DESIGN
