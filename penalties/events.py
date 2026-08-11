from django.db import transaction

from penalties.models import Penalty, PenaltyEvent


@transaction.atomic
def record_penalty_event(
    *,
    penalty: Penalty,
    event_type: PenaltyEvent.EventType,
    created_by,
    previous_amount=None,
    new_amount=None,
) -> PenaltyEvent:
    return PenaltyEvent.objects.create(
        penalty=penalty,
        event_type=event_type,
        created_by=created_by,
        previous_amount=previous_amount,
        new_amount=new_amount,
    )
