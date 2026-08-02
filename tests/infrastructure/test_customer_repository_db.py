"""DB-backed round-trip tests for DjangoCustomerRepository.

Requires a live PostgreSQL connection (pytest-django creates a real test
database via `DATABASE_URL`) — these will fail in an environment with no
reachable Postgres, which is expected and not a code defect.
"""

import pytest

from core.infrastructure.repositories.django_customer_repository import (
    DjangoCustomerRepository,
)

pytestmark = pytest.mark.django_db(transaction=True)


async def test_upsert_creates_a_new_customer() -> None:
    repository = DjangoCustomerRepository()

    customer = await repository.upsert(
        telegram_id=111, first_name="علی", last_name="محمدی", username="ali_m"
    )

    assert customer.id is not None
    assert customer.telegram_id == 111
    assert customer.first_name == "علی"
    assert customer.created_at is not None


async def test_upsert_is_idempotent_on_telegram_id() -> None:
    repository = DjangoCustomerRepository()

    first = await repository.upsert(
        telegram_id=222, first_name="علی", last_name=None, username=None
    )
    second = await repository.upsert(
        telegram_id=222, first_name="علی‌رضا", last_name="محمدی", username="alireza"
    )

    assert first.id == second.id
    assert second.first_name == "علی‌رضا"
    assert second.username == "alireza"


async def test_get_by_telegram_id_returns_none_when_missing() -> None:
    repository = DjangoCustomerRepository()
    assert await repository.get_by_telegram_id(999999) is None


async def test_get_by_telegram_id_finds_an_existing_customer() -> None:
    repository = DjangoCustomerRepository()
    created = await repository.upsert(
        telegram_id=333, first_name="رضا", last_name=None, username=None
    )

    found = await repository.get_by_telegram_id(333)

    assert found is not None
    assert found.id == created.id


async def test_update_phone_number_persists() -> None:
    repository = DjangoCustomerRepository()
    created = await repository.upsert(
        telegram_id=444, first_name="سارا", last_name=None, username=None
    )

    await repository.update_phone_number(created.id, "09123456789")

    updated = await repository.get_by_telegram_id(444)
    assert updated.phone_number == "09123456789"
