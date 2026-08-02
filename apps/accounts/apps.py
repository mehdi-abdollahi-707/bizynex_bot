from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Telegram customer identity (persistence for the `User` domain entity)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
