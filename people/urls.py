from django.urls import path

from people import views

app_name = "people"


urlpatterns = [
    path("", views.person_list, name="list"),
    path("new/", views.person_create, name="create"),
    path(
        "<uuid:public_id>/",
        views.person_detail,
        name="person-detail",
    ),
    path(
        "<uuid:public_id>/status/",
        views.person_change_status,
        name="change_status",
    ),
]
