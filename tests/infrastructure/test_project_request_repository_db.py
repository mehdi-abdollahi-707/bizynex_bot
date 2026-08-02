"""DB-backed round-trip tests for DjangoProjectRequestRepository.

Requires a live PostgreSQL connection — see test_customer_repository_db.py.
"""

import pytest

from core.domain.entities.attachment import ProjectAttachment
from core.domain.entities.estimation import Estimation
from core.domain.entities.project_request import ProjectRequest
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType
from core.infrastructure.repositories.django_customer_repository import (
    DjangoCustomerRepository,
)
from core.infrastructure.repositories.django_estimation_repository import (
    DjangoEstimationRepository,
)
from core.infrastructure.repositories.django_project_request_repository import (
    DjangoProjectRequestRepository,
)

pytestmark = pytest.mark.django_db(transaction=True)


async def _make_estimation() -> Estimation:
    customer = await DjangoCustomerRepository().upsert(
        telegram_id=666, first_name="علی", last_name=None, username=None
    )
    return await DjangoEstimationRepository().create(
        Estimation(
            customer_id=customer.id,
            service_type=ServiceType.TELEGRAM_BOT,
            answers={},
            price_range=PriceRange(5_000_000, 30_000_000),
            duration_range=DurationRange(7, 30),
        )
    )


async def test_create_persists_and_round_trips_every_field() -> None:
    estimation = await _make_estimation()
    repository = DjangoProjectRequestRepository()

    project_request = ProjectRequest(
        customer_id=estimation.customer_id,
        estimation_id=estimation.id,
        full_name="علی محمدی",
        phone_number="09123456789",
        company_name="شرکت نمونه",
        project_description="یک ربات فروش برای فروشگاه می‌خواهم.",
        proposed_budget="10 میلیون تومان",
        desired_timeline="2 هفته",
    )

    created = await repository.create(project_request)

    assert created.id is not None
    assert created.customer_id == estimation.customer_id
    assert created.estimation_id == estimation.id
    assert created.full_name == "علی محمدی"
    assert created.phone_number == "09123456789"
    assert created.company_name == "شرکت نمونه"
    assert created.project_description == "یک ربات فروش برای فروشگاه می‌خواهم."
    assert created.proposed_budget == "10 میلیون تومان"
    assert created.desired_timeline == "2 هفته"
    assert created.created_at is not None


async def test_create_allows_a_null_company_name() -> None:
    estimation = await _make_estimation()
    repository = DjangoProjectRequestRepository()

    created = await repository.create(
        ProjectRequest(
            customer_id=estimation.customer_id,
            estimation_id=estimation.id,
            full_name="رضا رضایی",
            phone_number="09121112233",
            company_name=None,
            project_description="توضیحات پروژه.",
            proposed_budget="5 میلیون",
            desired_timeline="1 هفته",
        )
    )

    assert created.company_name is None


async def test_add_attachment_persists_and_round_trips() -> None:
    estimation = await _make_estimation()
    project_request_repository = DjangoProjectRequestRepository()
    project_request = await project_request_repository.create(
        ProjectRequest(
            customer_id=estimation.customer_id,
            estimation_id=estimation.id,
            full_name="علی محمدی",
            phone_number="09123456789",
            project_description="توضیحات.",
            proposed_budget="10 میلیون",
            desired_timeline="2 هفته",
        )
    )

    attachment = await project_request_repository.add_attachment(
        ProjectAttachment(
            project_request_id=project_request.id,
            kind="document",
            telegram_file_id="FILE_ID_1",
            telegram_file_unique_id="UNIQUE_1",
            file_name="brief.pdf",
            mime_type="application/pdf",
            file_size=2048,
        )
    )

    assert attachment.id is not None
    assert attachment.project_request_id == project_request.id
    assert attachment.kind == "document"
    assert attachment.telegram_file_id == "FILE_ID_1"
    assert attachment.file_name == "brief.pdf"
    assert attachment.uploaded_at is not None


async def test_project_request_estimation_link_is_one_to_one() -> None:
    """A single Estimation can back at most one ProjectRequest (Phase 2's
    schema decision — every request references a real, unique estimate).
    """
    from django.db import IntegrityError

    estimation = await _make_estimation()
    repository = DjangoProjectRequestRepository()

    await repository.create(
        ProjectRequest(
            customer_id=estimation.customer_id,
            estimation_id=estimation.id,
            full_name="اول",
            phone_number="09121112233",
            project_description="اولین درخواست.",
            proposed_budget="5 میلیون",
            desired_timeline="1 هفته",
        )
    )

    with pytest.raises(IntegrityError):
        await repository.create(
            ProjectRequest(
                customer_id=estimation.customer_id,
                estimation_id=estimation.id,
                full_name="دوم",
                phone_number="09121112244",
                project_description="دومین درخواست با همان برآورد.",
                proposed_budget="6 میلیون",
                desired_timeline="1 هفته",
            )
        )
