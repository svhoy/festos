import pytest

from accounts.models import User
from people.models import MembershipStatus, Person
from people.services import (
    change_membership_status,
    create_person,
)


@pytest.mark.django_db
def test_create_person():
    person = create_person(
        first_name="Max",
        last_name="Mustermann",
    )

    assert person.pk is not None
    assert person.first_name == "Max"
    assert person.last_name == "Mustermann"
    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_change_membership_status_to_passive():
    person = create_person(
        first_name="Max",
        last_name="Mustermann",
    )

    result = change_membership_status(
        person=person,
        status=MembershipStatus.PASSIVE,
    )

    assert result.membership_status == MembershipStatus.PASSIVE

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.PASSIVE


@pytest.mark.django_db
def test_change_membership_status_to_left():
    person = create_person(
        first_name="Max",
        last_name="Mustermann",
    )

    result = change_membership_status(
        person=person,
        status=MembershipStatus.LEFT,
    )

    assert result.membership_status == MembershipStatus.LEFT

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.LEFT


@pytest.mark.django_db
def test_change_membership_status_does_nothing_if_status_is_unchanged():
    person = create_person(
        first_name="Max",
        last_name="Mustermann",
    )

    result = change_membership_status(
        person=person,
        status=MembershipStatus.ACTIVE,
    )

    assert result.pk == person.pk

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_create_person_with_membership_status():
    person = create_person(
        first_name="Max",
        last_name="Mustermann",
        membership_status=MembershipStatus.PASSIVE,
    )

    assert person.membership_status == MembershipStatus.PASSIVE


@pytest.mark.django_db
def test_create_person_can_link_user():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    person = create_person(
        first_name="Max",
        last_name="Mustermann",
        user=user,
    )

    assert person.user == user
