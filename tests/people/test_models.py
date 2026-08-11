import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from people.models import MembershipStatus, Person

User = get_user_model()


@pytest.mark.django_db
def test_person_can_be_created():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    assert person.first_name == "Max"
    assert person.last_name == "Mustermann"
    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_person_gets_unique_public_id():
    first = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )
    second = Person.objects.create(
        first_name="Peter",
        last_name="Müller",
    )

    assert isinstance(first.public_id, uuid.UUID)
    assert isinstance(second.public_id, uuid.UUID)
    assert first.public_id != second.public_id


@pytest.mark.django_db
def test_person_string_representation():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    assert str(person) == "Max Mustermann"


@pytest.mark.django_db
def test_person_is_active_by_default():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_person_can_be_passive():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
        membership_status=MembershipStatus.PASSIVE,
    )

    assert person.membership_status == MembershipStatus.PASSIVE


@pytest.mark.django_db
def test_person_can_have_left_membership_status():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
        membership_status=MembershipStatus.LEFT,
    )

    assert person.membership_status == MembershipStatus.LEFT


@pytest.mark.django_db
def test_person_can_be_deactivated():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    person.membership_status = MembershipStatus.LEFT
    person.save()

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.LEFT


def test_membership_status_has_expected_choices():
    choices = dict(MembershipStatus.choices)
    print(choices)
    assert choices == {
        "Aktiv": "Active",
        "Passiv": "Passive",
        "Ausgetreten": "Left",
    }


@pytest.mark.django_db
def test_person_can_be_linked_to_user():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    person = Person.objects.create(
        user=user,
        first_name="Max",
        last_name="Mustermann",
    )

    assert person.user == user
    assert user.person == person


@pytest.mark.django_db
def test_user_can_only_be_linked_to_one_person():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    Person.objects.create(
        user=user,
        first_name="Max",
        last_name="Mustermann",
    )

    second_person = Person(
        user=user,
        first_name="Moritz",
        last_name="Muster",
    )

    with pytest.raises(IntegrityError):
        second_person.save()


@pytest.mark.django_db
def test_deleting_user_does_not_delete_person():
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    person = Person.objects.create(
        user=user,
        first_name="Max",
        last_name="Mustermann",
    )

    user.delete()

    person.refresh_from_db()

    assert Person.objects.filter(
        pk=person.pk,
    ).exists()

    assert person.user is None
