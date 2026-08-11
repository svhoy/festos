from decimal import Decimal

import pytest

from penalties.models import PenaltyCatalogEntry, PenaltyEvent
from penalties.queries import (
    get_active_catalog_entries,
    get_open_penalties,
    get_open_penalty_total,
    get_penalty_history,
)
from penalties.services import pay_penalties, remove_penalty


@pytest.mark.django_db
def test_get_open_penalties_returns_unpaid_penalties(
    person,
    penalty_factory,
):
    first = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    second = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    penalties = get_open_penalties(person=person)

    assert set(penalties) == {
        first,
        second,
    }


@pytest.mark.django_db
def test_get_open_penalties_excludes_paid_penalties(
    person,
    penalty_factory,
    user,
):
    paid = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    open_penalty = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    pay_penalties(
        penalties=[paid],
        paid_by=user,
    )

    penalties = get_open_penalties(
        person=person,
    )

    assert list(penalties) == [
        open_penalty,
    ]


@pytest.mark.django_db
def test_get_open_penalties_excludes_removed_penalties(
    person,
    penalty_factory,
    spiess_user,
):
    removed = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    open_penalty = penalty_factory(
        person=person,
        amount=Decimal("15.00"),
    )

    remove_penalty(
        penalty=removed,
        removed_by=spiess_user,
    )

    penalties = get_open_penalties(
        person=person,
    )

    assert list(penalties) == [
        open_penalty,
    ]


@pytest.mark.django_db
def test_get_open_penalty_total(
    person,
    penalty_factory,
):
    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )
    penalty_factory(
        person=person,
        amount=Decimal("15.50"),
    )

    total = get_open_penalty_total(
        person=person,
    )

    assert total == Decimal("25.50")


@pytest.mark.django_db
def test_get_open_penalty_total_is_zero_when_nothing_is_open(
    person,
):
    total = get_open_penalty_total(
        person=person,
    )

    assert total == Decimal("0.00")


@pytest.mark.django_db
def test_get_active_catalog_entries_excludes_inactive_entries(
    catalog_entry,
):
    inactive = PenaltyCatalogEntry.objects.create(
        name="Inaktiv",
        amount=Decimal("20.00"),
        is_active=False,
    )

    entries = get_active_catalog_entries()

    assert catalog_entry in entries
    assert inactive not in entries


@pytest.mark.django_db
def test_get_penalty_history_returns_all_penalties(
    person,
    penalty_factory,
):
    first = penalty_factory(person=person)
    second = penalty_factory(person=person)

    history = get_penalty_history(
        person=person,
    )

    assert set(history) == {
        first,
        second,
    }


@pytest.mark.django_db
def test_get_active_catalog_entries_only_returns_active_entries(
    penalty_catalog_entry_factory,
):
    active = penalty_catalog_entry_factory(
        is_active=True,
    )

    penalty_catalog_entry_factory(
        is_active=False,
    )

    result = get_active_catalog_entries()

    assert list(result) == [active]


@pytest.mark.django_db
def test_penalty_history_contains_paid_penalty(
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

    history = get_penalty_history(
        person=person,
    )

    history_penalty = history.get(
        pk=penalty.pk,
    )

    assert history_penalty == penalty

    assert history_penalty.payments.exists()

    assert history_penalty.events.filter(
        event_type=PenaltyEvent.EventType.PAID,
    ).exists()
