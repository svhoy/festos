from datetime import datetime, timezone
from decimal import Decimal

import pytest

from penalties.services import remove_penalty
from people.models import Person
from ranking.queries import (
    get_total_ranking,
    get_yearly_ranking,
)


@pytest.mark.django_db
def test_yearly_ranking_sums_penalties_for_selected_year(
    person,
    penalty_factory,
):
    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    penalty_2025 = penalty_factory(
        person=person,
        amount=Decimal("20.00"),
    )

    penalty_2025.issued_at = datetime(
        2025,
        6,
        1,
        tzinfo=timezone.utc,
    )
    penalty_2025.save(update_fields=["issued_at"])

    ranking = get_yearly_ranking(
        year=2026,
    )

    assert list(ranking) == [person]
    assert ranking[0].total_penalty_amount == Decimal("10.00")


@pytest.mark.django_db
def test_yearly_ranking_counts_paid_penalties(
    person,
    penalty_factory,
    spiess_user,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("30.00"),
    )

    from penalties.services import pay_penalties

    pay_penalties(
        penalties=[penalty],
        paid_by=spiess_user,
    )

    ranking = get_yearly_ranking(
        year=2026,
    )

    assert list(ranking) == [person]
    assert ranking[0].total_penalty_amount == Decimal("30.00")


@pytest.mark.django_db
def test_yearly_ranking_excludes_removed_penalties(
    person,
    penalty_factory,
    spiess_user,
):
    removed = penalty_factory(
        person=person,
        amount=Decimal("50.00"),
    )

    penalty_factory(
        person=person,
        amount=Decimal("20.00"),
    )

    remove_penalty(
        penalty=removed,
        removed_by=spiess_user,
    )

    ranking = get_yearly_ranking(
        year=2026,
    )

    assert list(ranking) == [person]
    assert ranking[0].total_penalty_amount == Decimal("20.00")


@pytest.mark.django_db
def test_yearly_ranking_orders_by_total_descending(
    person,
    penalty_factory,
):
    other_person = Person.objects.create(
        first_name="Erika",
        last_name="Musterfrau",
    )

    penalty_factory(
        person=person,
        amount=Decimal("20.00"),
    )

    penalty_factory(
        person=other_person,
        amount=Decimal("50.00"),
    )

    ranking = list(
        get_yearly_ranking(
            year=2026,
        )
    )

    assert ranking == [
        other_person,
        person,
    ]

    assert ranking[0].total_penalty_amount == Decimal("50.00")
    assert ranking[1].total_penalty_amount == Decimal("20.00")


@pytest.mark.django_db
def test_total_ranking_includes_all_years(
    person,
    penalty_factory,
):
    penalty_2025 = penalty_factory(
        person=person,
        amount=Decimal("40.00"),
    )

    penalty_2025.issued_at = datetime(
        2025,
        6,
        1,
        tzinfo=timezone.utc,
    )
    penalty_2025.save(update_fields=["issued_at"])

    penalty_factory(
        person=person,
        amount=Decimal("60.00"),
    )

    ranking = get_total_ranking()

    assert list(ranking) == [person]
    assert ranking[0].total_penalty_amount == Decimal("100.00")


@pytest.mark.django_db
def test_total_ranking_sums_multiple_penalties_per_person(
    person,
    penalty_factory,
):
    other_person = Person.objects.create(
        first_name="Erika",
        last_name="Musterfrau",
    )

    penalty_factory(
        person=person,
        amount=Decimal("30.00"),
    )

    penalty_factory(
        person=person,
        amount=Decimal("40.00"),
    )

    penalty_factory(
        person=other_person,
        amount=Decimal("50.00"),
    )

    ranking = list(get_total_ranking())

    assert ranking == [
        person,
        other_person,
    ]

    assert ranking[0].total_penalty_amount == Decimal("70.00")
    assert ranking[1].total_penalty_amount == Decimal("50.00")


@pytest.mark.django_db
def test_total_ranking_excludes_person_with_only_removed_penalties(
    person,
    penalty_factory,
    spiess_user,
):
    penalty = penalty_factory(
        person=person,
        amount=Decimal("50.00"),
    )

    remove_penalty(
        penalty=penalty,
        removed_by=spiess_user,
    )

    ranking = list(get_total_ranking())

    assert ranking == [person]
    assert ranking[0].total_penalty_amount == Decimal("0.00")
