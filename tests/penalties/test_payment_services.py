from decimal import Decimal

import pytest

from penalties.models import PenaltyEvent
from penalties.services import pay_all_open_penalties, pay_penalties


@pytest.mark.django_db
def test_single_penalty_can_be_paid(
    penalty,
    user,
):
    payment = pay_penalties(
        penalties=[penalty],
        paid_by=user,
    )

    assert payment.amount == penalty.amount
    assert list(payment.penalties.all()) == [penalty]


@pytest.mark.django_db
def test_multiple_penalties_can_be_paid_together(
    penalty_factory,
    person,
    user,
):
    first = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    second = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    payment = pay_penalties(
        penalties=[first, second],
        paid_by=user,
    )

    assert payment.amount == Decimal("25.00")
    assert set(payment.penalties.all()) == {
        first,
        second,
    }


@pytest.mark.django_db
def test_all_open_penalties_can_be_paid(
    penalty_factory,
    person,
    user,
):
    first = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    second = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    payment = pay_all_open_penalties(
        person=person,
        paid_by=user,
    )

    assert payment.amount == Decimal("25.00")
    assert set(payment.penalties.all()) == {
        first,
        second,
    }


@pytest.mark.django_db
def test_already_paid_penalty_cannot_be_paid_again(
    penalty,
    user,
):
    pay_penalties(
        penalties=[penalty],
        paid_by=user,
    )

    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[penalty],
            paid_by=user,
        )


@pytest.mark.django_db
def test_penalties_from_different_people_cannot_be_paid_together(
    penalty_factory,
    person,
    other_person,
    user,
):
    first = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    second = penalty_factory(
        person=other_person,
        amount=Decimal("15.00"),
    )

    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[first, second],
            paid_by=user,
        )


@pytest.mark.django_db
def test_empty_penalty_list_cannot_be_paid(user):
    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[],
            paid_by=user,
        )


@pytest.mark.django_db
def test_pay_all_open_penalties_ignores_already_paid_penalties(
    penalty_factory,
    person,
    user,
):
    paid_penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    open_penalty = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    pay_penalties(
        penalties=[paid_penalty],
        paid_by=user,
    )

    payment = pay_all_open_penalties(
        person=person,
        paid_by=user,
    )

    assert payment.amount == Decimal("15.00")
    assert set(payment.penalties.all()) == {
        open_penalty,
    }


@pytest.mark.django_db
def test_paying_penalty_creates_paid_event(
    penalty,
    user,
):
    pay_penalties(
        penalties=[penalty],
        paid_by=user,
    )

    event = penalty.events.get(
        event_type=PenaltyEvent.EventType.PAID,
    )

    assert event.created_by == user


@pytest.mark.django_db
def test_paying_multiple_penalties_creates_paid_event_for_each(
    penalty_factory,
    person,
    user,
):
    first = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    second = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    pay_penalties(
        penalties=[first, second],
        paid_by=user,
    )

    assert (
        first.events.filter(
            event_type=PenaltyEvent.EventType.PAID,
        ).count()
        == 1
    )

    assert (
        second.events.filter(
            event_type=PenaltyEvent.EventType.PAID,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_failed_payment_does_not_create_events(
    penalty_factory,
    person,
    other_person,
    user,
):
    first = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    second = penalty_factory(
        person=other_person,
        amount=Decimal("15.00"),
    )

    with pytest.raises(ValueError):
        pay_penalties(
            penalties=[first, second],
            paid_by=user,
        )

    assert not first.events.exists()
    assert not second.events.exists()
