from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ranking.queries import get_total_ranking


@login_required
def ranking(request):
    return render(
        request,
        "ranking/ranking.html",
        {
            "ranking": get_total_ranking(),
        },
    )
