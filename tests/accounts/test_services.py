import pytest
from django.contrib.auth import get_user_model

from accounts.roles import Role
from accounts.services import assign_role, get_role

User = get_user_model()


@pytest.mark.django_db
def test_user_can_be_assigned_spiess_role():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SPIESS,
    )

    user.refresh_from_db()

    assert get_role(user=user) == Role.SPIESS


@pytest.mark.django_db
def test_user_can_be_assigned_schuetze_role():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SCHUETZE,
    )

    assert get_role(user=user) == Role.SCHUETZE


@pytest.mark.django_db
def test_user_without_role_returns_none():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    assert get_role(user=user) is None


@pytest.mark.django_db
def test_assigning_new_role_replaces_previous_role():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SCHUETZE,
    )

    assign_role(
        user=user,
        role=Role.SPIESS,
    )

    user.refresh_from_db()

    assert get_role(user=user) == Role.SPIESS
    assert user.groups.count() == 1
