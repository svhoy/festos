from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from penalties.events import record_penalty_event
from penalties.models import Penalty, PenaltyCatalogEntry, PenaltyEvent
from penalties.services import issue_penalty
from people.models import Person

User = get_user_model()


@pytest.mark.django_db
def test_issue_penalty_creates_issued_event(
    spiess_user,
):
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    catalog_entry = PenaltyCatalogEntry.objects.create(
        name="Zu spät zum Antreten",
        amount=Decimal("5.00"),
    )

    penalty = issue_penalty(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=spiess_user,
    )

    events = penalty.events.all()

    assert events.count() == 1

    event = events.first()

    assert event.event_type == PenaltyEvent.EventType.ISSUED
    assert event.created_by == spiess_user
