"""Django ORM implementation of `CustomerRepository`."""

from __future__ import annotations

from apps.accounts.models import Customer as CustomerModel
from core.domain.entities.customer import Customer


class DjangoCustomerRepository:
    async def get_by_telegram_id(self, telegram_id: int) -> Customer | None:
        try:
            model = await CustomerModel.objects.aget(telegram_id=telegram_id)
        except CustomerModel.DoesNotExist:
            return None
        return _to_entity(model)

    async def upsert(
        self,
        *,
        telegram_id: int,
        first_name: str,
        last_name: str | None,
        username: str | None,
    ) -> Customer:
        model, _created = await CustomerModel.objects.aupdate_or_create(
            telegram_id=telegram_id,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
            },
        )
        return _to_entity(model)

    async def update_phone_number(self, customer_id: int, phone_number: str) -> None:
        await CustomerModel.objects.filter(id=customer_id).aupdate(phone_number=phone_number)


def _to_entity(model: CustomerModel) -> Customer:
    return Customer(
        id=model.id,
        telegram_id=model.telegram_id,
        first_name=model.first_name,
        last_name=model.last_name,
        username=model.username,
        phone_number=model.phone_number,
        created_at=model.created_at,
        last_interaction_at=model.last_interaction_at,
    )
