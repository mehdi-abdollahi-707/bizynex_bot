"""Root URL configuration."""

from django.conf import settings
from django.urls import path

from apps.bot.views import health_check, telegram_webhook

urlpatterns = [
    path(settings.WEBHOOK_PATH.lstrip("/"), telegram_webhook, name="telegram-webhook"),
    path("health/", health_check, name="health-check"),
]
