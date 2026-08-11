from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from accounts.permissions import can_manage_penalty_for_person
from penalties.events import record_penalty_event
from penalties.models import (
    Payment,
    Penalty,
    PenaltyCatalogEntry,
    PenaltyEvent,
)
from people.models import Person


def get_open_penalties(person):
    return Penalty.objects.filter(
        person=person,
        payments__isnull=True,
    )


@transaction.atomic
def issue_penalty(
    *,
    person,
    catalog_entry,
    issued_by,
) -> Penalty:
    if not can_manage_penalty_for_person(
        user=issued_by,
        person=person,
    ):
        raise PermissionError("Diese Strafe darf nicht ausgesprochen werden.")

    penalty = Penalty.objects.create(
        person=person,
        catalog_entry=catalog_entry,
        amount=catalog_entry.amount,
        issued_by=issued_by,
    )

    record_penalty_event(
        penalty=penalty,
        event_type=PenaltyEvent.EventType.ISSUED,
        created_by=issued_by,
    )

    return penalty


@transaction.atomic
def update_penalty_amount(
    *,
    penalty: Penalty,
    amount: Decimal,
    updated_by,
) -> Penalty:
    penalty.refresh_from_db()

    if amount <= Decimal("0.00"):
        raise ValueError("Der Strafbetrag muss größer als 0 sein.")

    if penalty.removed_at is not None:
        raise ValueError("Eine entfernte Strafe kann nicht geändert werden.")

    if penalty.payments.exists():
        raise ValueError("Eine bezahlte Strafe kann nicht geändert werden.")

    if penalty.amount == amount:
        return penalty

    previous_amount = penalty.amount

    penalty.amount = amount
    penalty.save(
        update_fields=["amount"],
    )

    record_penalty_event(
        penalty=penalty,
        event_type=PenaltyEvent.EventType.AMOUNT_CHANGED,
        created_by=updated_by,
        previous_amount=previous_amount,
        new_amount=amount,
    )

    return penalty


@transaction.atomic
def pay_penalties(
    *,
    penalties: list[Penalty],
    paid_by,
) -> Payment:
    if not penalties:
        raise ValueError("Es muss mindestens eine Strafe bezahlt werden.")

    people = {penalty.person_id for penalty in penalties}

    if len(people) != 1:
        raise ValueError(
            "Strafen verschiedener Personen können nicht gemeinsam bezahlt werden."
        )
    for penalty in penalties:
        if penalty.removed_at is not None:
            raise ValueError("Eine entfernte Strafe kann nicht bezahlt werden.")

        if penalty.payments.exists():
            raise ValueError("Eine oder mehrere Strafen wurden bereits bezahlt.")

    total_amount = sum(
        (penalty.amount for penalty in penalties),
        Decimal("0.00"),
    )

    payment = Payment.objects.create(
        amount=total_amount,
        paid_by=paid_by,
    )

    payment.penalties.set(penalties)

    for penalty in penalties:
        record_penalty_event(
            penalty=penalty,
            event_type=PenaltyEvent.EventType.PAID,
            created_by=paid_by,
        )

    return payment


@transaction.atomic
def pay_all_open_penalties(
    *,
    person: Person,
    paid_by,
) -> Payment:
    open_penalties = Penalty.objects.filter(
        person=person,
    ).exclude(
        payments__isnull=False,
    )

    return pay_penalties(
        penalties=open_penalties,
        paid_by=paid_by,
    )


@transaction.atomic
def remove_penalty(
    *,
    penalty: Penalty,
    removed_by,
) -> Penalty:
    if penalty.removed_at is not None:
        raise ValueError("Die Strafe wurde bereits entfernt.")

    if penalty.payments.exists():
        raise ValueError("Eine bezahlte Strafe kann nicht entfernt werden.")

    if not can_manage_penalty_for_person(
        user=removed_by,
        person=penalty.person,
    ):
        raise PermissionError("Diese Strafe darf nicht entfernt werden.")

    penalty.removed_at = timezone.now()
    penalty.removed_by = removed_by

    penalty.save(
        update_fields=[
            "removed_at",
            "removed_by",
        ],
    )

    record_penalty_event(
        penalty=penalty,
        event_type=PenaltyEvent.EventType.REMOVED,
        created_by=removed_by,
    )

    return penalty


def create_catalog_entry(
    *,
    name: str,
    description: str = "",
    amount: Decimal,
) -> PenaltyCatalogEntry:
    if amount <= Decimal("0.00"):
        raise ValueError("Der Strafbetrag muss größer als 0 sein.")

    return PenaltyCatalogEntry.objects.create(
        name=name,
        description=description,
        amount=amount,
    )


def update_catalog_entry(
    *,
    catalog_entry: PenaltyCatalogEntry,
    name: str,
    description: str = "",
    amount: Decimal,
) -> PenaltyCatalogEntry:
    if amount <= Decimal("0.00"):
        raise ValueError("Der Strafbetrag muss größer als 0 sein.")

    catalog_entry.name = name
    catalog_entry.description = description
    catalog_entry.amount = amount

    catalog_entry.save(
        update_fields=[
            "name",
            "description",
            "amount",
            "updated_at",
        ],
    )

    return catalog_entry


def deactivate_catalog_entry(
    *,
    catalog_entry: PenaltyCatalogEntry,
) -> None:
    catalog_entry.is_active = False
    catalog_entry.save(
        update_fields=["is_active", "updated_at"],
    )


def activate_catalog_entry(
    *,
    catalog_entry: PenaltyCatalogEntry,
) -> None:
    catalog_entry.is_active = True
    catalog_entry.save(
        update_fields=["is_active", "updated_at"],
    )
