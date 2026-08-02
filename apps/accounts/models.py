"""Persistence model for Telegram customer accounts."""

from __future__ import annotations

from django.db import models


class Customer(models.Model):
    """A Telegram user who has messaged the bot."""

    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} ({self.telegram_id})"
