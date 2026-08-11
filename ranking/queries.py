from decimal import Decimal

from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce

from people.models import Person


def get_yearly_ranking(
    *,
    year: int,
):
    return Person.objects.annotate(
        total_penalty_amount=Coalesce(
            Sum(
                "penalties__amount",
                filter=Q(
                    penalties__issued_at__year=year,
                    penalties__removed_at__isnull=True,
                ),
            ),
            Value(Decimal("0.00")),
        ),
    ).order_by(
        "-total_penalty_amount",
        "last_name",
        "first_name",
    )


def get_total_ranking():
    return Person.objects.annotate(
        total_penalty_amount=Coalesce(
            Sum(
                "penalties__amount",
                filter=Q(
                    penalties__removed_at__isnull=True,
                ),
            ),
            Value(Decimal("0.00")),
        ),
    ).order_by(
        "-total_penalty_amount",
        "last_name",
        "first_name",
    )
