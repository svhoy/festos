import pytest
from django.urls import reverse

from accounts.role_permissions import setup_role_permissions


@pytest.mark.django_db
def test_home_page_is_accessible(
    client,
    user,
):
    client.force_login(user)

    response = client.get(
        reverse("home"),
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_spiess_sees_catalog_navigation(
    client,
    spiess_user,
):
    setup_role_permissions()

    client.force_login(spiess_user)

    response = client.get(
        reverse("home"),
    )

    content = response.content.decode()

    assert "Strafenkatalog" in content


@pytest.mark.django_db
def test_schuetze_does_not_see_catalog_navigation(
    client,
    schuetze_user,
):
    setup_role_permissions()

    client.force_login(schuetze_user)

    response = client.get(
        reverse("home"),
    )

    content = response.content.decode()

    assert "Strafenkatalog" not in content
