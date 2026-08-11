from django.urls import path

from penalties.views import (
    catalog_activate_view,
    catalog_create_view,
    catalog_deactivate_view,
    catalog_list_view,
    catalog_update_view,
    issue_penalty_view,
    pay_all_penalties_view,
    pay_penalties_view,
    remove_penalty_view,
)

app_name = "penalties"


urlpatterns = [
    path(
        "catalog/",
        catalog_list_view,
        name="catalog-list",
    ),
    path(
        "catalog/new/",
        catalog_create_view,
        name="catalog-create",
    ),
    path(
        "catalog/<int:pk>/edit/",
        catalog_update_view,
        name="catalog-update",
    ),
    path(
        "catalog/<int:pk>/activate/",
        catalog_activate_view,
        name="catalog-activate",
    ),
    path(
        "catalog/<int:pk>/deactivate/",
        catalog_deactivate_view,
        name="catalog-deactivate",
    ),
    path(
        "r/<uuid:public_id>/issue/",
        issue_penalty_view,
        name="issue",
    ),
    path(
        "strafen/<int:pk>/entfernen/",
        remove_penalty_view,
        name="remove",
    ),
    path(
        "personen/<uuid:public_id>/bezahlen/",
        pay_penalties_view,
        name="pay",
    ),
    path(
        "personen/<uuid:public_id>/alle-bezahlen/",
        pay_all_penalties_view,
        name="pay-all",
    ),
]
