"""Smoke tests verifying the Django project boots with valid configuration."""

from django.conf import settings


def test_django_settings_configured() -> None:
    assert settings.configured is True


def test_installed_apps_exclude_admin_and_auth() -> None:
    assert "django.contrib.admin" not in settings.INSTALLED_APPS
    assert "django.contrib.auth" not in settings.INSTALLED_APPS


def test_expected_apps_are_installed() -> None:
    assert "apps.accounts" in settings.INSTALLED_APPS
    assert "apps.requests" in settings.INSTALLED_APPS
    assert "apps.bot" in settings.INSTALLED_APPS


def test_language_and_timezone_are_persian() -> None:
    assert settings.LANGUAGE_CODE == "fa"
    assert settings.TIME_ZONE == "Asia/Tehran"
