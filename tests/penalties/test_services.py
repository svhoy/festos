from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from penalties.models import Penalty, PenaltyCatalogEntry, PenaltyEvent
from penalties.services import (
    issue_penalty,
    pay_penalties,
    remove_penalty,
    update_catalog_entry,
    update_penalty_amount,
)
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
def test_issue_penalty_copies_catalog_amount(
    person,
    catalog_entry,
    spiess_user,
):
    catalog_entry.amount = Decimal("25.00")
    catalog_entry.save()

    penalty = issue_penalty(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=spiess_user,
    )

    assert penalty.amount == Decimal("25.00")
    catalog_entry.amount = Decimal("25.00")
    catalog_entry.save()

    penalty = issue_penalty(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=spiess_user,
    )

    assert penalty.amount == Decimal("25.00")


@pytest.mark.django_db
def test_issue_penalty_creates_issued_event(
    person,
    catalog_entry,
    spiess_user,
):
    penalty = issue_penalty(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=spiess_user,
    )

    event = penalty.events.get(
        event_type=PenaltyEvent.EventType.ISSUED,
    )

    assert event.created_by == spiess_user
    penalty = issue_penalty(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=spiess_user,
    )

    event = penalty.events.get(
        event_type=PenaltyEvent.EventType.ISSUED,
    )

    assert event.created_by == spiess_user


@pytest.mark.django_db
def test_remove_penalty_marks_penalty_as_removed(
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

    assert penalty.removed_at is not None
    assert penalty.removed_by == spiess_user


@pytest.mark.django_db
def test_paid_penalty_cannot_be_removed(
    penalty,
    user,
):
    pay_penalties(
        penalties=[penalty],
        paid_by=user,
    )

    with pytest.raises(ValueError):
        remove_penalty(
            penalty=penalty,
            removed_by=user,
        )


@pytest.mark.django_db
def test_penalty_amount_can_be_updated(
    penalty,
    user,
):
    update_penalty_amount(
        penalty=penalty,
        amount=Decimal("15.00"),
        updated_by=user,
    )

    penalty.refresh_from_db()

    assert penalty.amount == Decimal("15.00")


@pytest.mark.django_db
def test_penalty_amount_update_creates_event(
    penalty,
    user,
):
    update_penalty_amount(
        penalty=penalty,
        amount=Decimal("15.00"),
        updated_by=user,
    )

    event = penalty.events.get(
        event_type=PenaltyEvent.EventType.AMOUNT_CHANGED,
    )

    assert event.created_by == user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-1.00"),
    ],
)
def test_penalty_amount_cannot_be_invalid(
    penalty,
    user,
    amount,
):
    with pytest.raises(ValueError):
        update_penalty_amount(
            penalty=penalty,
            amount=amount,
            updated_by=user,
        )


@pytest.mark.django_db
def test_paid_penalty_amount_cannot_be_updated(
    penalty,
    user,
):
    pay_penalties(
        penalties=[penalty],
        paid_by=user,
    )

    with pytest.raises(ValueError):
        update_penalty_amount(
            penalty=penalty,
            amount=Decimal("15.00"),
            updated_by=user,
        )


@pytest.mark.django_db
def test_removed_penalty_amount_cannot_be_updated(
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

    with pytest.raises(ValueError):
        update_penalty_amount(
            penalty=penalty,
            amount=Decimal("15.00"),
            updated_by=spiess_user,
        )


@pytest.mark.django_db
def test_update_catalog_entry(
    penalty_catalog_entry_factory,
):
    entry = penalty_catalog_entry_factory(
        name="Zu spät",
        description="Alt",
        amount=Decimal("10.00"),
    )

    update_catalog_entry(
        catalog_entry=entry,
        name="Sehr zu spät",
        description="Neu",
        amount=Decimal("25.00"),
    )

    entry.refresh_from_db()

    assert entry.name == "Sehr zu spät"
    assert entry.description == "Neu"
    assert entry.amount == Decimal("25.00")
    assert entry.is_active is True


@pytest.mark.django_db
def test_update_catalog_entry_rejects_zero_amount(
    penalty_catalog_entry_factory,
):
    entry = penalty_catalog_entry_factory(
        amount=Decimal("10.00"),
    )

    with pytest.raises(ValueError):
        update_catalog_entry(
            catalog_entry=entry,
            name="Zu spät",
            description="",
            amount=Decimal("0.00"),
        )


@pytest.mark.django_db
def test_update_catalog_entry_does_not_change_existing_penalty(
    penalty_catalog_entry_factory,
    person,
    spiess_user,
):
    entry = penalty_catalog_entry_factory(
        amount=Decimal("10.00"),
    )

    penalty = issue_penalty(
        person=person,
        catalog_entry=entry,
        issued_by=spiess_user,
    )

    update_catalog_entry(
        catalog_entry=entry,
        name="Zu spät",
        description="Geändert",
        amount=Decimal("25.00"),
    )

    penalty.refresh_from_db()

    assert penalty.amount == Decimal("10.00")


@pytest.mark.django_db
def test_spiess_can_remove_penalty_from_other_person(
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

    assert penalty.removed_at is not None
    assert penalty.removed_by == spiess_user


@pytest.mark.django_db
def test_remove_penalty_creates_removed_event(
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

    event = penalty.events.get()

    assert event.event_type == PenaltyEvent.EventType.REMOVED
    assert event.created_by == spiess_user


@pytest.mark.django_db
def test_spiess_cannot_remove_own_penalty(
    penalty_factory,
    spiess_user,
    person,
):
    person.user = spiess_user
    person.save(update_fields=["user"])

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    with pytest.raises(PermissionError):
        remove_penalty(
            penalty=penalty,
            removed_by=spiess_user,
        )


@pytest.mark.django_db
def test_schuetze_cannot_remove_penalty(
    penalty_factory,
    schuetze_user,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    with pytest.raises(PermissionError):
        remove_penalty(
            penalty=penalty,
            removed_by=schuetze_user,
        )


@pytest.mark.django_db
def test_removed_penalty_cannot_be_removed_again(
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

    with pytest.raises(ValueError):
        remove_penalty(
            penalty=penalty,
            removed_by=spiess_user,
        )
