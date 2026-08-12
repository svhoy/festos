from decimal import Decimal

from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce

from penalties.models import Penalty
from people.models import MembershipStatus, Person


def get_penalty_years():
    return (
        Penalty.objects.filter(
            removed_at__isnull=True,
        )
        .values_list(
            "issued_at__year",
            flat=True,
        )
        .distinct()
        .order_by("-issued_at__year")
    )


def get_yearly_ranking(
    *,
    year: int,
):
    return (
        Person.objects.filter(
            membership_status=MembershipStatus.ACTIVE,
        )
        .annotate(
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
        )
        .order_by(
            "-total_penalty_amount",
            "last_name",
            "first_name",
        )
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
