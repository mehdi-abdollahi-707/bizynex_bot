"""Persistence model for aiogram FSM state (PostgreSQL-backed, no Redis).

Render's free-tier web service has no persistent memory across restarts —
every cold start after idle sleep is effectively a fresh process — so FSM
state (which menu step a customer is on, their in-progress answers) must
live in the database, not in memory. The custom `BaseStorage` implementation
that reads/writes this table is built in Phase 3.
"""

from __future__ import annotations

from django.db import models


class TelegramFSMState(models.Model):
    """Mirrors aiogram's `StorageKey` so conversation state survives restarts."""

    bot_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    # aiogram's StorageKey.thread_id is Optional[int]; stored as 0 instead of
    # NULL because Postgres treats NULL as distinct in unique constraints,
    # which would silently break uniqueness for every non-threaded chat.
    thread_id = models.BigIntegerField(default=0)
    destiny = models.CharField(max_length=32, default="default")

    state = models.CharField(max_length=255, null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "telegram_fsm_states"
        constraints = [
            models.UniqueConstraint(
                fields=["bot_id", "chat_id", "user_id", "thread_id", "destiny"],
                name="unique_fsm_storage_key",
            ),
        ]

    def __str__(self) -> str:
        return f"FSM(chat={self.chat_id}, user={self.user_id}, state={self.state})"
