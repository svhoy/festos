from decimal import Decimal

import pytest
from django.urls import reverse

from penalties.models import Penalty
from ranking.queries import get_total_ranking


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
    assert "30.00" in content
