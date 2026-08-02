"""Customer entity: a Telegram user Bizynex is talking to."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Customer:
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    phone_number: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    last_interaction_at: datetime | None = None

    @property
    def display_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
