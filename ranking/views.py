from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ranking.queries import (
    get_penalty_years,
    get_total_ranking,
    get_yearly_ranking,
)


@login_required
def ranking(request):
    current_year = date.today().year

    try:
        selected_year = int(request.GET.get("year", current_year))
    except TypeError, ValueError:
        selected_year = current_year

    return render(
        request,
        "ranking/ranking.html",
        {
            "total_ranking": get_total_ranking(),
            "yearly_ranking": get_yearly_ranking(
                year=selected_year,
            ),
            "selected_year": selected_year,
            "available_years": get_penalty_years(),
        },
    )
