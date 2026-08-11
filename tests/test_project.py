from django.apps import apps
from django.conf import settings


def test_django_settings_are_loaded():
    assert settings.configured
    assert settings.SECRET_KEY


def test_festos_apps_are_installed():
    expected_apps = {
        "core",
        "accounts",
        "people",
        "penalties",
        "ranking",
        "audit",
    }

    installed_apps = {config.name for config in apps.get_app_configs()}

    assert expected_apps <= installed_apps
