from django.apps import AppConfig


class BotConfig(AppConfig):
    """aiogram presentation layer: routers, handlers, keyboards, FSM storage."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.bot"
    label = "bot"
