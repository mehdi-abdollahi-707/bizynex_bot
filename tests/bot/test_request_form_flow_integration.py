"""Full project request form conversation walkthroughs, exercised at the
handler level — field sequencing, validation, skips, file attachment,
per-field editing, cancellation, and submission — with only the DB-backed
repository calls and the admin `Bot.send_message` call mocked.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from apps.bot.handlers import request_form
from apps.bot.keyboards.callback_data import (
    RequestFormEditFieldCallback,
    RequestFormStartCallback,
)
from apps.bot.states.request_form import RequestFormFlow
from core.domain.entities.estimation import Estimation
from core.domain.entities.project_request import ProjectRequest
from core.domain.value_objects.duration_range import DurationRange
from core.domain.value_objects.price_range import PriceRange
from core.domain.value_objects.service_type import ServiceType


@pytest.fixture
def owned_estimation(fake_customer) -> Estimation:
    return Estimation(
        id=7,
        customer_id=fake_customer.id,
        service_type=ServiceType.WORDPRESS_WEBSITE,
        answers={},
        price_range=PriceRange(25_000_000, 120_000_000),
        duration_range=DurationRange(21, 49),
    )


@pytest.fixture
def mock_repositories(monkeypatch, owned_estimation):
    created_requests: list[ProjectRequest] = []
    created_attachments: list = []

    async def fake_get_by_id(estimation_id: int):
        return owned_estimation if estimation_id == owned_estimation.id else None

    async def fake_create(project_request: ProjectRequest) -> ProjectRequest:
        created = ProjectRequest(
            id=len(created_requests) + 1,
            customer_id=project_request.customer_id,
            estimation_id=project_request.estimation_id,
            full_name=project_request.full_name,
            phone_number=project_request.phone_number,
            company_name=project_request.company_name,
            project_description=project_request.project_description,
            proposed_budget=project_request.proposed_budget,
            desired_timeline=project_request.desired_timeline,
        )
        created_requests.append(created)
        return created

    async def fake_add_attachment(attachment):
        created_attachments.append(attachment)
        return attachment

    monkeypatch.setattr(request_form._estimation_repository, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(request_form._project_request_repository, "create", fake_create)
    monkeypatch.setattr(
        request_form._project_request_repository, "add_attachment", fake_add_attachment
    )

    return {"requests": created_requests, "attachments": created_attachments}


async def _start(state, make_callback, fake_customer, owned_estimation):
    callback = make_callback()
    await request_form.start_request_form(
        callback,
        RequestFormStartCallback(estimation_id=owned_estimation.id),
        state,
        fake_customer,
    )
    return callback


async def test_start_rejects_an_estimation_belonging_to_someone_else(
    make_state, make_callback, fake_customer, mock_repositories
):
    state = make_state()
    callback = make_callback()

    await request_form.start_request_form(
        callback, RequestFormStartCallback(estimation_id=999), state, fake_customer
    )

    assert await state.get_state() is None
    text = callback.message.edit_text.call_args.args[0]
    assert "معتبر نیست" in text


async def test_full_happy_path_with_skip_and_attachment(
    make_state, make_callback, make_message, fake_customer, owned_estimation, mock_repositories
):
    state = make_state()
    bot = AsyncMock()

    await _start(state, make_callback, fake_customer, owned_estimation)
    assert await state.get_state() == RequestFormFlow.full_name.state

    await request_form.handle_full_name(make_message("علی محمدی"), state)
    assert await state.get_state() == RequestFormFlow.phone_number.state

    await request_form.handle_phone_number(make_message("09123456789"), state)
    assert await state.get_state() == RequestFormFlow.company_name.state

    # Skip company name via the button, not text.
    skip_callback = make_callback()
    await request_form.handle_skip_company_name(skip_callback, state)
    assert (await state.get_data())["company_name"] is None
    assert await state.get_state() == RequestFormFlow.project_description.state

    await request_form.handle_project_description(
        make_message("می‌خواهم یک فروشگاه اینترنتی برای فروش لباس راه‌اندازی کنم."), state
    )
    assert await state.get_state() == RequestFormFlow.proposed_budget.state

    await request_form.handle_proposed_budget(make_message("حدود 60 میلیون تومان"), state)
    assert await state.get_state() == RequestFormFlow.desired_timeline.state

    await request_form.handle_desired_timeline(make_message("یک و نیم ماه"), state)
    assert await state.get_state() == RequestFormFlow.attachment.state

    document = SimpleNamespace(
        file_id="F1",
        file_unique_id="U1",
        file_name="brief.pdf",
        mime_type="application/pdf",
        file_size=1234,
    )
    await request_form.handle_attachment_document(make_message(document=document), state)

    # Attachment was the last field -> straight to confirm.
    assert await state.get_state() == RequestFormFlow.confirm.state
    data = await state.get_data()
    assert data["attachment"]["telegram_file_id"] == "F1"

    # Submit.
    submit_callback = make_callback()
    await request_form.handle_submit(submit_callback, state, fake_customer, bot)

    assert await state.get_state() is None
    success_text = submit_callback.message.edit_text.call_args.args[0]
    assert "با موفقیت ثبت شد" in success_text

    assert len(mock_repositories["requests"]) == 1
    created = mock_repositories["requests"][0]
    assert created.full_name == "علی محمدی"
    assert created.phone_number == "09123456789"
    assert created.company_name is None
    assert len(mock_repositories["attachments"]) == 1

    bot.send_message.assert_awaited_once()
    admin_text = bot.send_message.call_args.kwargs["text"]
    assert "علی محمدی" in admin_text
    bot.send_document.assert_awaited_once()


async def test_invalid_phone_number_does_not_advance(
    make_state, make_message, fake_customer, owned_estimation, mock_repositories, make_callback
):
    state = make_state()
    await _start(state, make_callback, fake_customer, owned_estimation)
    await request_form.handle_full_name(make_message("علی محمدی"), state)

    bad_message = make_message("not a phone number")
    await request_form.handle_phone_number(bad_message, state)

    assert await state.get_state() == RequestFormFlow.phone_number.state
    bad_message.answer.assert_awaited_once()
    error_text = bad_message.answer.call_args.args[0]
    assert "معتبر نیست" in error_text


async def test_edit_full_name_returns_directly_to_summary(
    make_state, make_message, make_callback, fake_customer, owned_estimation, mock_repositories
):
    state = make_state()
    await _start(state, make_callback, fake_customer, owned_estimation)
    await request_form.handle_full_name(make_message("علی محمدی"), state)
    await request_form.handle_phone_number(make_message("09123456789"), state)
    await request_form.handle_skip_company_name(make_callback(), state)
    await request_form.handle_project_description(make_message("توضیحات پروژه نمونه است."), state)
    await request_form.handle_proposed_budget(make_message("10 میلیون"), state)
    await request_form.handle_desired_timeline(make_message("1 ماه"), state)
    await request_form.handle_skip_attachment(make_callback(), state)
    assert await state.get_state() == RequestFormFlow.confirm.state

    # Open the edit menu, choose full_name.
    edit_menu_callback = make_callback()
    await request_form.show_edit_menu(edit_menu_callback)

    choose_field_callback = make_callback()
    await request_form.handle_edit_field_choice(
        choose_field_callback, RequestFormEditFieldCallback(field="full_name"), state
    )
    assert await state.get_state() == RequestFormFlow.full_name.state
    assert (await state.get_data())["editing"] is True

    # Re-enter the name -> should go straight back to the summary, not
    # continue through phone_number/company_name/... again.
    await request_form.handle_full_name(make_message("رضا رضایی"), state)

    assert await state.get_state() == RequestFormFlow.confirm.state
    data = await state.get_data()
    assert data["full_name"] == "رضا رضایی"
    assert data["phone_number"] == "09123456789"  # untouched
    assert data["editing"] is False


async def test_cancel_from_summary_clears_state_and_shows_main_menu(
    make_state, make_message, make_callback, fake_customer, owned_estimation, mock_repositories
):
    state = make_state()
    await _start(state, make_callback, fake_customer, owned_estimation)
    await request_form.handle_full_name(make_message("علی محمدی"), state)
    await request_form.handle_phone_number(make_message("09123456789"), state)
    await request_form.handle_skip_company_name(make_callback(), state)
    await request_form.handle_project_description(make_message("توضیحات پروژه نمونه است."), state)
    await request_form.handle_proposed_budget(make_message("10 میلیون"), state)
    await request_form.handle_desired_timeline(make_message("1 ماه"), state)
    await request_form.handle_skip_attachment(make_callback(), state)

    cancel_callback = make_callback()
    await request_form.handle_cancel(cancel_callback, state, fake_customer)

    assert await state.get_state() is None
    assert len(mock_repositories["requests"]) == 0
    text = cancel_callback.message.edit_text.call_args.args[0]
    assert "Bizynex" in text


async def test_double_submit_second_call_is_a_no_op(
    make_state, make_message, make_callback, fake_customer, owned_estimation, mock_repositories
):
    state = make_state()
    bot = AsyncMock()
    await _start(state, make_callback, fake_customer, owned_estimation)
    await request_form.handle_full_name(make_message("علی محمدی"), state)
    await request_form.handle_phone_number(make_message("09123456789"), state)
    await request_form.handle_skip_company_name(make_callback(), state)
    await request_form.handle_project_description(make_message("توضیحات پروژه نمونه است."), state)
    await request_form.handle_proposed_budget(make_message("10 میلیون"), state)
    await request_form.handle_desired_timeline(make_message("1 ماه"), state)
    await request_form.handle_skip_attachment(make_callback(), state)

    first_submit = make_callback()
    await request_form.handle_submit(first_submit, state, fake_customer, bot)
    assert len(mock_repositories["requests"]) == 1

    # A second submit tap after the first already cleared state (e.g. a
    # slow double-tap) must not create a second ProjectRequest.
    second_submit = make_callback()
    await request_form.handle_submit(second_submit, state, fake_customer, bot)
    assert len(mock_repositories["requests"]) == 1
