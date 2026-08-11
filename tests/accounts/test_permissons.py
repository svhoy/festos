import pytest
from django.contrib.auth import get_user_model

from accounts.permissions import (
    can_manage_penalty_for_person,
    is_admin,
    is_kommandant,
    is_spiess,
)
from accounts.role_permissions import setup_role_permissions
from accounts.roles import Role
from accounts.services import assign_role

User = get_user_model()


@pytest.mark.django_db
def test_spiess_is_spiess():
    user = User.objects.create_user(
        username="spiess",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SPIESS,
    )

    assert is_spiess(user=user) is True


@pytest.mark.django_db
def test_schuetze_is_not_spiess():
    user = User.objects.create_user(
        username="schuetze",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SCHUETZE,
    )

    assert is_spiess(user=user) is False


@pytest.mark.django_db
def test_oberleutnant_is_kommandant():
    user = User.objects.create_user(
        username="olt",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.OBERLEUTNANT,
    )

    assert is_kommandant(user=user) is True


@pytest.mark.django_db
def test_leutnant_is_kommandant():
    user = User.objects.create_user(
        username="lt",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.LEUTNANT,
    )

    assert is_kommandant(user=user) is True


@pytest.mark.django_db
def test_admin_is_not_kommandant():
    user = User.objects.create_user(
        username="admin",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.ADMIN,
    )

    assert is_kommandant(user=user) is False


@pytest.mark.django_db
def test_spiess_can_penalize_other_person(
    spiess_user,
    person,
):
    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=spiess_user,
            person=person,
        )
            is True
    )


@pytest.mark.django_db
def test_spiess_cannot_penalize_self(
    spiess_user,
    person,
):
    person.user = spiess_user
    person.save()

    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=spiess_user,
            person=person,
        )
            is False
    )


@pytest.mark.django_db
def test_oberleutnant_can_penalize_spiess(
    oberleutnant_user,
    spiess_person,
):
    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=oberleutnant_user,
            person=spiess_person,
        )
            is True
    )


@pytest.mark.django_db
def test_oberleutnant_cannot_penalize_schuetze(
    oberleutnant_user,
    person,
):
    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=oberleutnant_user,
            person=person,
        )
            is False
    )


@pytest.mark.django_db
def test_leutnant_can_penalize_spiess(
    leutnant_user,
    spiess_person,
):
    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=leutnant_user,
            person=spiess_person,
        )
            is True
    )


@pytest.mark.django_db
def test_leutnant_cannot_penalize_schuetze(
    leutnant_user,
    person,
):
    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=leutnant_user,
            person=person,
        )
            is False
    )


@pytest.mark.django_db
def test_schuetze_cannot_penalize_anyone(
    schuetze_user,
    spiess_person,
):
    setup_role_permissions()
    assert (
            can_manage_penalty_for_person(
            user=schuetze_user,
            person=spiess_person,
        )
            is False
    )
