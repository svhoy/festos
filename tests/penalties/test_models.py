from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import models

from penalties.events import record_penalty_event
from penalties.models import Penalty, PenaltyCatalogEntry, PenaltyEvent
from penalties.services import pay_penalties, remove_penalty
from people.models import Person

User = get_user_model()


@pytest.mark.django_db
def test_create_penalty():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    catalog_entry = PenaltyCatalogEntry.objects.create(
        name="Zu spät zum Antreten",
        amount=Decimal("5.00"),
    )

    user = User.objects.create_user(
        username="spiess",
        password="test-password",
    )

    penalty = Penalty.objects.create(
        person=person,
        catalog_entry=catalog_entry,
        amount=catalog_entry.amount,
        issued_by=user,
    )

    assert penalty.person == person
    assert penalty.catalog_entry == catalog_entry
    assert penalty.amount == Decimal("5.00")
    assert penalty.issued_by == user
    assert not penalty.payments.exists()


@pytest.mark.django_db
def test_catalog_entry_cannot_be_deleted_when_used():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    catalog_entry = PenaltyCatalogEntry.objects.create(
        name="Zu spät zum Antreten",
        amount=5,
    )

    user = User.objects.create_user(
        username="spiess",
        password="test-password",
    )

    Penalty.objects.create(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=user,
        amount=catalog_entry.amount,
    )

    with pytest.raises(
        models.ProtectedError,
    ):
        catalog_entry.delete()


@pytest.mark.django_db
def test_person_cannot_be_deleted_when_penalty_exists():
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    catalog_entry = PenaltyCatalogEntry.objects.create(
        name="Zu spät zum Antreten",
        amount=5,
    )

    user = User.objects.create_user(
        username="spiess",
        password="test-password",
    )

    Penalty.objects.create(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=user,
        amount=catalog_entry.amount,
    )

    with pytest.raises(
        models.ProtectedError,
    ):
        person.delete()


@pytest.mark.django_db
def test_penalty_status_is_issued(
    penalty_factory,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    assert penalty.status == PenaltyEvent.EventType.ISSUED


@pytest.mark.django_db
def test_penalty_status_stays_issued_after_amount_change(
    penalty_factory,
    spiess_user,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    record_penalty_event(
        penalty=penalty,
        event_type=PenaltyEvent.EventType.AMOUNT_CHANGED,
        created_by=spiess_user,
        previous_amount=Decimal("10.00"),
        new_amount=Decimal("15.00"),
    )

    penalty.refresh_from_db()

    assert penalty.status == PenaltyEvent.EventType.ISSUED


@pytest.mark.django_db
def test_penalty_status_is_paid_after_payment(
    penalty_factory,
    spiess_user,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    pay_penalties(
        penalties=[penalty],
        paid_by=spiess_user,
    )

    penalty.refresh_from_db()

    assert penalty.status == PenaltyEvent.EventType.PAID


@pytest.mark.django_db
def test_penalty_status_is_removed_after_removal(
    penalty_factory,
    spiess_user,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    remove_penalty(
        penalty=penalty,
        removed_by=spiess_user,
    )

    penalty.refresh_from_db()

    assert penalty.status == PenaltyEvent.EventType.REMOVED
