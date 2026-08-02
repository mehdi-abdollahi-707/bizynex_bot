from django.apps import AppConfig


class RequestsConfig(AppConfig):
    """Project requests, price estimations, and their uploaded attachments."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.requests"
    label = "requests"
