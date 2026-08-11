import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from accounts.role_permissions import setup_role_permissions
from accounts.roles import ROLE_LABELS, Role
from accounts.services import assign_role

User = get_user_model()


@pytest.fixture
def setup_roles():
    setup_role_permissions()


@pytest.mark.django_db
def test_people_permissions_exist():
    assert Permission.objects.filter(
        content_type__app_label="people",
        codename="view_person",
    ).exists()

    assert Permission.objects.filter(
        content_type__app_label="people",
        codename="manage_person",
    ).exists()


@pytest.mark.django_db
def test_setup_role_permissions_creates_role_groups():
    setup_role_permissions()

    assert Group.objects.filter(
        name=ROLE_LABELS[Role.ADMIN],
    ).exists()

    assert Group.objects.filter(
        name=ROLE_LABELS[Role.SPIESS],
    ).exists()


@pytest.mark.django_db
def test_admin_has_manage_person_permission():
    setup_role_permissions()
    user = User.objects.create_user(
        username="admin",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.ADMIN,
    )

    assert user.has_perm(
        "people.manage_person",
    )


@pytest.mark.django_db
def test_schuetze_does_not_have_manage_person_permission():
    setup_role_permissions()
    user = User.objects.create_user(
        username="schuetze",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SCHUETZE,
    )

    assert not user.has_perm(
        "people.manage_person",
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "permission", "expected"),
    [
        (
            Role.ADMIN,
            "people.view_person",
            True,
        ),
        (
            Role.ADMIN,
            "people.manage_person",
            True,
        ),
        (
            Role.SPIESS,
            "people.view_person",
            True,
        ),
        (
            Role.SPIESS,
            "people.manage_person",
            True,
        ),
        (
            Role.OBERLEUTNANT,
            "people.view_person",
            True,
        ),
        (
            Role.OBERLEUTNANT,
            "people.manage_person",
            False,
        ),
        (
            Role.LEUTNANT,
            "people.view_person",
            True,
        ),
        (
            Role.LEUTNANT,
            "people.manage_person",
            False,
        ),
        (
            Role.SCHUETZE,
            "people.view_person",
            True,
        ),
        (
            Role.SCHUETZE,
            "people.manage_person",
            False,
        ),
    ],
)
def test_role_permissions(
    role,
    permission,
    expected,
):
    setup_role_permissions()

    user = User.objects.create_user(
        username=f"user-{role}",
        password="test-password",
    )

    assign_role(
        user=user,
        role=role,
    )

    assert user.has_perm(permission) is expected


@pytest.mark.django_db
def test_user_without_role_has_no_management_permission():
    setup_role_permissions()
    user = User.objects.create_user(
        username="unassigned",
        password="test-password",
    )

    assert not user.has_perm(
        "people.manage_person",
    )
