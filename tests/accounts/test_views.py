import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from people.models import Person

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        ),
    )

    assert response.status_code == 302

    assert response.url.startswith(
        reverse("accounts:login"),
    )

    assert "next=" in response.url


@pytest.mark.django_db
def test_authenticated_user_can_access_person_detail(client):
    user = User.objects.create_user(
        username="max",
        password="test-password",
    )

    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    client.force_login(user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        ),
    )

    assert response.status_code == 200
    assert "Max Mustermann" in response.content.decode()


@pytest.mark.django_db
def test_user_can_login(client):
    User.objects.create_user(
        username="max",
        password="correct-password",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "max",
            "password": "correct-password",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("people:list")


@pytest.mark.django_db
def test_login_redirects_to_original_page(client):
    User.objects.create_user(
        username="max",
        password="correct-password",
    )

    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    detail_url = reverse(
        "people:person-detail",
        kwargs={
            "public_id": person.public_id,
        },
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "max",
            "password": "correct-password",
            "next": detail_url,
        },
    )

    assert response.status_code == 302
    assert response.url == detail_url


@pytest.mark.django_db
def test_user_can_logout(client):
    User.objects.create_user(
        username="max",
        password="correct-password",
    )

    client.login(
        username="max",
        password="correct-password",
    )

    response = client.post(
        reverse("accounts:logout"),
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:login")


@pytest.mark.django_db
def test_login_page_is_accessible(client):
    response = client.get(
        reverse("accounts:login"),
    )

    assert response.status_code == 200
    assert "Anmeldung" in response.content.decode()
