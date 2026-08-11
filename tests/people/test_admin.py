from django.contrib import admin

from people.models import Person


def test_person_is_registered_in_admin():
    assert Person in admin.site._registry
