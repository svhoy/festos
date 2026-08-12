from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from django.urls import reverse

from people.models import MembershipStatus, Person


@pytest.mark.django_db
def test_ranking_page_is_accessible(
    client,
    spiess_user,
):
    client.force_login(spiess_user)

    response = client.get(
        reverse("ranking:ranking"),
    )

    assert response.status_code == 200
    assert "Ranking" in response.content.decode()


@pytest.mark.django_db
def test_ranking_page_shows_people_and_totals(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    penalty_factory(
        person=person,
        amount=Decimal("30.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse("ranking:ranking"),
    )

    content = response.content.decode()

    assert str(person) in content
    assert "30 €" in content


@pytest.mark.django_db
def test_ranking_page_shows_people_without_penalties(
    client,
    spiess_user,
    person,
):
    client.force_login(spiess_user)

    response = client.get(
        reverse("ranking:ranking"),
    )

    content = response.content.decode()

    assert str(person) in content
    assert "0 €" in content


@pytest.mark.django_db
def test_ranking_page_shows_selected_year_ranking(
    client,
    spiess_user,
    person,
    penalty_factory,
):
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
    penalty_2025.save(
        update_fields=["issued_at"],
    )

    penalty_factory(
        person=person,
        amount=Decimal("50.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse("ranking:ranking"),
        {"year": 2025},
    )

    assert response.status_code == 200

    yearly_ranking = response.context["yearly_ranking"]

    assert list(yearly_ranking) == [person]
    assert yearly_ranking[0].total_penalty_amount == Decimal("20.00")


@pytest.mark.django_db
def test_ranking_page_defaults_to_current_year(
    client,
    spiess_user,
):
    client.force_login(spiess_user)

    response = client.get(
        reverse("ranking:ranking"),
    )

    assert response.context["selected_year"] == date.today().year


@pytest.mark.django_db
def test_ranking_page_shows_only_active_people_in_yearly_ranking(
    client,
    spiess_user,
    person,
):
    passive_person = Person.objects.create(
        first_name="Erika",
        last_name="Musterfrau",
        membership_status=MembershipStatus.PASSIVE,
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse("ranking:ranking"),
        {"year": 2026},
    )

    yearly_ranking = response.context["yearly_ranking"]

    assert person in yearly_ranking
    assert passive_person not in yearly_ranking
