"""Persistence models for project requests, estimations, and uploaded files."""

from __future__ import annotations

from django.db import models

from core.domain.value_objects.service_type import ServiceType as DomainServiceType

SERVICE_TYPE_CHOICES = [(member.value, member.label_fa) for member in DomainServiceType]


class Estimation(models.Model):
    """A computed price/duration estimate the customer received for one service."""

    customer = models.ForeignKey(
        "accounts.Customer", on_delete=models.CASCADE, related_name="estimations"
    )
    service_type = models.CharField(max_length=32, choices=SERVICE_TYPE_CHOICES)

    # Raw configurator answers (question key -> chosen option), kept as JSON
    # so each service's question set can evolve without a schema migration.
    answers = models.JSONField(default=dict, blank=True)

    price_min_toman = models.PositiveIntegerField()
    price_max_toman = models.PositiveIntegerField()
    duration_min_days = models.PositiveIntegerField()
    duration_max_days = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "estimations"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Estimation({self.service_type}, customer={self.customer_id})"


class ProjectRequest(models.Model):
    """A customer's submitted request for a quoted project, following an estimation."""

    customer = models.ForeignKey(
        "accounts.Customer", on_delete=models.CASCADE, related_name="project_requests"
    )
    estimation = models.OneToOneField(
        Estimation, on_delete=models.PROTECT, related_name="project_request"
    )

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    project_description = models.TextField()
    proposed_budget = models.CharField(max_length=255)
    desired_timeline = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_requests"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ProjectRequest({self.full_name}, {self.estimation.service_type})"


class AttachmentKind(models.TextChoices):
    DOCUMENT = "document", "Document"
    PHOTO = "photo", "Photo"


class ProjectAttachment(models.Model):
    """A file the customer attached to a request — Telegram's reference only."""

    project_request = models.ForeignKey(
        ProjectRequest, on_delete=models.CASCADE, related_name="attachments"
    )
    kind = models.CharField(
        max_length=20, choices=AttachmentKind.choices, default=AttachmentKind.DOCUMENT
    )
    telegram_file_id = models.CharField(max_length=255)
    telegram_file_unique_id = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_attachments"

    def __str__(self) -> str:
        return self.file_name or self.telegram_file_unique_id
