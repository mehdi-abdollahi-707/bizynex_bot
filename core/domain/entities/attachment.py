"""ProjectAttachment entity: an optional file the customer attached to a request.

Only Telegram's file reference is stored, never the bytes — the free-tier
deployment target has no persistent disk, and Telegram already keeps the
file on its own servers indefinitely via `telegram_file_id`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectAttachment:
    project_request_id: int
    kind: str  # "document" or "photo" — which Telegram send method to re-use it with
    telegram_file_id: str
    telegram_file_unique_id: str
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    id: int | None = None
    uploaded_at: datetime | None = None
