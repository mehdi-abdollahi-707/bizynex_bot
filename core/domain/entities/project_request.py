"""ProjectRequest entity: a customer's submitted request for a quoted project."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectRequest:
    customer_id: int
    estimation_id: int
    full_name: str
    phone_number: str
    project_description: str
    proposed_budget: str
    desired_timeline: str
    company_name: str | None = None
    id: int | None = None
    created_at: datetime | None = None
