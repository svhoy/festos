from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from accounts.role_permissions import setup_role_permissions
from penalties.models import Payment, Penalty, PenaltyCatalogEntry, PenaltyEvent
from penalties.services import pay_penalties
from people.models import Person


@pytest.fixture
def catalog_entry(db):
    return PenaltyCatalogEntry.objects.create(
        name="Zu spät zum Antreten",
        amount=Decimal("5.00"),
    )


@pytest.fixture
def penalty(person, user, catalog_entry):
    return Penalty.objects.create(
        person=person,
        catalog_entry=catalog_entry,
        amount=catalog_entry.amount,
        issued_by=user,
    )


@pytest.mark.django_db
def test_single_penalty_can_be_paid_with_pay_penalties(
    penalty_factory,
    spiess_user,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    payment = pay_penalties(
        penalties=[penalty],
        paid_by=spiess_user,
    )

    assert payment.amount == Decimal("10.00")
    assert payment.penalties.filter(pk=penalty.pk).exists()


@pytest.mark.django_db
def test_multiple_penalties_can_be_paid(
    penalty_factory,
    spiess_user,
    person,
):
    penalty_one = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    penalty_two = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    payment = pay_penalties(
        penalties=[
            penalty_one,
            penalty_two,
        ],
        paid_by=spiess_user,
    )

    assert payment.amount == Decimal("25.00")
    assert payment.paid_by == spiess_user

    assert set(payment.penalties.all()) == {
        penalty_one,
        penalty_two,
    }


@pytest.mark.django_db
def test_already_paid_penalty_cannot_be_paid_again(
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

    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[penalty],
            paid_by=spiess_user,
        )

    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_no_penalties_cannot_be_paid(
    spiess_user,
):
    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[],
            paid_by=spiess_user,
        )


@pytest.mark.django_db
def test_multiple_penalties_create_one_payment(
    penalty_factory,
    spiess_user,
    person,
):
    penalty_one = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    penalty_two = penalty_factory(
        person=person,
        amount=Decimal("20.00"),
    )

    pay_penalties(
        penalties=[penalty_one, penalty_two],
        paid_by=spiess_user,
    )

    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_multiple_penalties_create_paid_events(
    penalty_factory,
    spiess_user,
    person,
):
    penalty_one = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    penalty_two = penalty_factory(
        person=person,
        amount=Decimal("20.00"),
    )

    pay_penalties(
        penalties=[penalty_one, penalty_two],
        paid_by=spiess_user,
    )

    assert (
        penalty_one.events.filter(
            event_type=PenaltyEvent.EventType.PAID,
        ).count()
        == 1
    )

    assert (
        penalty_two.events.filter(
            event_type=PenaltyEvent.EventType.PAID,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_removed_penalty_cannot_be_paid(
    penalty_factory,
    spiess_user,
    person,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
        removed_at=timezone.now(),
        removed_by=spiess_user,
    )

    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[penalty],
            paid_by=spiess_user,
        )


@pytest.mark.django_db
def test_spiess_can_pay_selected_penalties(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty_one = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    penalty_two = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    client.force_login(spiess_user)

    response = client.post(
        reverse(
            "penalties:pay",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "penalties": [
                penalty_one.pk,
                penalty_two.pk,
            ],
        },
    )

    assert response.status_code == 302

    payment = Payment.objects.get()

    assert payment.amount == Decimal("25.00")
    assert set(payment.penalties.all()) == {
        penalty_one,
        penalty_two,
    }


@pytest.mark.django_db
def test_schuetze_cannot_pay_penalties(
    client,
    schuetze_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(schuetze_user)

    response = client.post(
        reverse(
            "penalties:pay",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "penalties": [penalty.pk],
        },
    )

    assert response.status_code == 403
    assert Payment.objects.count() == 0
