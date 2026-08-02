"""Repository interface for ProjectRequest and ProjectAttachment persistence."""

from __future__ import annotations

from typing import Protocol

from core.domain.entities.attachment import ProjectAttachment
from core.domain.entities.project_request import ProjectRequest


class ProjectRequestRepository(Protocol):
    async def create(self, project_request: ProjectRequest) -> ProjectRequest: ...

    async def add_attachment(self, attachment: ProjectAttachment) -> ProjectAttachment: ...
