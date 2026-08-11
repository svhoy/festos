from django.urls import path

from ranking.views import ranking

app_name = "ranking"

urlpatterns = [
    path(
        "",
        ranking,
        name="ranking",
    ),
]
