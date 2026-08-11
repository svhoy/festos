from decimal import Decimal

from django.db.models import QuerySet, Sum

from penalties.models import Penalty, PenaltyCatalogEntry
from people.models import Person


def get_open_penalties(
    *,
    person: Person,
) -> QuerySet[Penalty]:
    return Penalty.objects.filter(
        person=person,
        removed_at__isnull=True,
        payments__isnull=True,
    ).distinct()


def get_open_penalty_total(
    *,
    person: Person,
) -> Decimal:
    total = get_open_penalties(
        person=person,
    ).aggregate(
        total=Sum("amount"),
    )["total"]

    return total or Decimal("0.00")


def get_active_catalog_entries() -> QuerySet[PenaltyCatalogEntry]:
    return PenaltyCatalogEntry.objects.filter(
        is_active=True,
    )


def get_penalty_history(
    *,
    person: Person,
) -> QuerySet[Penalty]:
    return (
        Penalty.objects.filter(person=person)
        .select_related(
            "catalog_entry",
            "issued_by",
            "removed_by",
        )
        .prefetch_related(
            "events",
            "payments",
        )
    )
