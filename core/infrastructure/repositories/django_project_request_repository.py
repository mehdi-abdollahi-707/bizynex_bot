"""Django ORM implementation of `ProjectRequestRepository`."""

from __future__ import annotations

from apps.requests.models import ProjectAttachment as ProjectAttachmentModel
from apps.requests.models import ProjectRequest as ProjectRequestModel
from core.domain.entities.attachment import ProjectAttachment
from core.domain.entities.project_request import ProjectRequest


class DjangoProjectRequestRepository:
    async def create(self, project_request: ProjectRequest) -> ProjectRequest:
        model = await ProjectRequestModel.objects.acreate(
            customer_id=project_request.customer_id,
            estimation_id=project_request.estimation_id,
            full_name=project_request.full_name,
            phone_number=project_request.phone_number,
            company_name=project_request.company_name,
            project_description=project_request.project_description,
            proposed_budget=project_request.proposed_budget,
            desired_timeline=project_request.desired_timeline,
        )
        return _to_entity(model)

    async def add_attachment(self, attachment: ProjectAttachment) -> ProjectAttachment:
        model = await ProjectAttachmentModel.objects.acreate(
            project_request_id=attachment.project_request_id,
            kind=attachment.kind,
            telegram_file_id=attachment.telegram_file_id,
            telegram_file_unique_id=attachment.telegram_file_unique_id,
            file_name=attachment.file_name,
            mime_type=attachment.mime_type,
            file_size=attachment.file_size,
        )
        return _to_attachment_entity(model)


def _to_entity(model: ProjectRequestModel) -> ProjectRequest:
    return ProjectRequest(
        id=model.id,
        customer_id=model.customer_id,
        estimation_id=model.estimation_id,
        full_name=model.full_name,
        phone_number=model.phone_number,
        company_name=model.company_name,
        project_description=model.project_description,
        proposed_budget=model.proposed_budget,
        desired_timeline=model.desired_timeline,
        created_at=model.created_at,
    )


def _to_attachment_entity(model: ProjectAttachmentModel) -> ProjectAttachment:
    return ProjectAttachment(
        id=model.id,
        project_request_id=model.project_request_id,
        kind=model.kind,
        telegram_file_id=model.telegram_file_id,
        telegram_file_unique_id=model.telegram_file_unique_id,
        file_name=model.file_name,
        mime_type=model.mime_type,
        file_size=model.file_size,
        uploaded_at=model.uploaded_at,
    )
