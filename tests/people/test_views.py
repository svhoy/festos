import uuid
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.permissions import can_manage_penalty_for_person, is_spiess
from accounts.role_permissions import setup_role_permissions
from penalties.services import get_open_penalties, pay_penalties
from people.models import MembershipStatus, Person

User = get_user_model()


@pytest.mark.django_db
def test_person_list_is_accessible(client):
    user = User.objects.create_user(
        username="test-user",
        password="test-password",
    )

    client.force_login(user)

    response = client.get(
        reverse("people:list"),
    )

    assert response.status_code == 200
    assert "Personen" in response.content.decode()


@pytest.mark.django_db
def test_person_list_displays_person(client):
    user = User.objects.create_user(
        username="test-user",
        password="test-password",
    )

    client.force_login(user)
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    response = client.get(
        reverse("people:list"),
    )

    assert response.status_code == 200
    assert str(person) in response.content.decode()


@pytest.mark.django_db
def test_person_detail_displays_open_penalties(
    client,
    user,
    person,
    penalty_factory,
):
    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    assert response.status_code == 200
    assert b"10.00" in response.content


@pytest.mark.django_db
def test_person_detail_is_accessible(client):
    user = User.objects.create_user(
        username="test-user",
        password="test-password",
    )
    client.force_login(user)
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

    assert response.status_code == 200
    assert "Max Mustermann" in response.content.decode()


@pytest.mark.django_db
def test_person_detail_requires_login(
    client,
    person,
):
    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_person_detail_returns_404_for_unknown_public_id(
    client,
    user,
):
    client.force_login(user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": "00000000-0000-0000-0000-000000000000",
            },
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_person_can_be_created(client):
    response = client.post(
        reverse("people:create"),
        {
            "first_name": "Max",
            "last_name": "Mustermann",
            "membership_status": MembershipStatus.ACTIVE,
        },
    )

    assert response.status_code == 302

    person = Person.objects.get(
        first_name="Max",
        last_name="Mustermann",
    )

    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_person_cannot_be_created_without_first_name(client):
    response = client.post(
        reverse("people:create"),
        {
            "first_name": "",
            "last_name": "Mustermann",
            "membership_status": MembershipStatus.ACTIVE,
        },
    )

    assert response.status_code == 200
    assert Person.objects.count() == 0


@pytest.mark.django_db
def test_person_status_can_be_changed(client):
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    response = client.post(
        reverse(
            "people:change_status",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "membership_status": MembershipStatus.PASSIVE,
        },
    )

    assert response.status_code == 302

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.PASSIVE


@pytest.mark.django_db
def test_person_status_rejects_invalid_value(client):
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    response = client.post(
        reverse(
            "people:change_status",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "membership_status": "something-invalid",
        },
    )

    assert response.status_code == 400

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_person_status_cannot_be_changed_with_get(client):
    person = Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )

    response = client.get(
        reverse(
            "people:change_status",
            kwargs={
                "public_id": person.public_id,
            },
        ),
    )

    assert response.status_code == 405

    person.refresh_from_db()

    assert person.membership_status == MembershipStatus.ACTIVE


@pytest.mark.django_db
def test_spiess_sees_issue_penalty_button(
    client,
    spiess_user,
    person,
):
    setup_role_permissions()
    assert (
        spiess_user.has_perm(
            "penalties.issue_penalty",
        )
        is True
    )
    client.force_login(spiess_user)
    spiess_user.groups.all()
    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    assert response.status_code == 200
    assert "Strafe aussprechen" in response.content.decode()


@pytest.mark.django_db
def test_schuetze_does_not_see_issue_penalty_button(
    client,
    schuetze_user,
    person,
):
    client.force_login(schuetze_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    assert response.status_code == 200
    assert "Strafe aussprechen" not in response.content.decode()


@pytest.mark.django_db
def test_spiess_sees_active_penalty_catalog_entries(
    client,
    spiess_user,
    person,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()
    catalog_entry = penalty_catalog_entry_factory(
        name="Zu spät",
        amount=Decimal("10.00"),
        is_active=True,
    )

    penalty_catalog_entry_factory(
        name="Deaktivierte Strafe",
        amount=Decimal("50.00"),
        is_active=False,
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()
    assert catalog_entry.name in content
    assert "Deaktivierte Strafe" not in content


@pytest.mark.django_db
def test_spiess_sees_payable_penalties(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()
    assert f'name="penalties"' in content
    assert f'value="{penalty.pk}"' in content


@pytest.mark.django_db
def test_paid_penalty_is_not_payable_again(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    pay_penalties(
        penalties=[penalty],
        paid_by=spiess_user,
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert f'name="penalties" value="{penalty.pk}"' not in content


@pytest.mark.django_db
def test_spiess_sees_payable_penalty_checkboxes(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert 'name="penalties"' in content
    assert f'value="{penalty.pk}"' in content


@pytest.mark.django_db
def test_schuetze_does_not_see_payable_penalty_checkboxes(
    client,
    schuetze_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(schuetze_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert f"{penalty.amount}" in content
    assert 'name="penalties"' not in content


@pytest.mark.django_db
def test_user_without_role_does_not_see_payable_penalty_checkboxes(
    client,
    user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert f"{penalty.amount}" in content
    assert 'name="penalties"' not in content


@pytest.mark.django_db
def test_schuetze_does_not_see_pay_penalties_button(
    client,
    schuetze_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(schuetze_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    assert "Ausgewählte Strafen bezahlen" not in response.content.decode()


@pytest.mark.django_db
def test_spiess_sees_pay_penalties_button(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    assert "Ausgewählte Strafen bezahlen" in response.content.decode()


@pytest.mark.django_db
def test_issue_penalty_updates_open_penalty_total(
    client,
    spiess_user,
    person,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()

    catalog_entry = penalty_catalog_entry_factory(
        name="Zu spät",
        amount=Decimal("10.00"),
        is_active=True,
    )

    client.force_login(spiess_user)

    response = client.post(
        reverse(
            "penalties:issue",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "catalog_entry": catalog_entry.pk,
        },
    )

    assert response.status_code == 200

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert "10.00" in content
    assert "10 €" in content


@pytest.mark.django_db
def test_issue_penalty_adds_penalty_to_history(
    client,
    spiess_user,
    person,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()

    catalog_entry = penalty_catalog_entry_factory(
        name="Zu spät",
        amount=Decimal("10.00"),
        is_active=True,
    )

    client.force_login(spiess_user)

    client.post(
        reverse(
            "penalties:issue",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "catalog_entry": catalog_entry.pk,
        },
    )

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert "Historie" in content
    assert "Zu spät" in content
    assert "10.00" in content


@pytest.mark.django_db
def test_pay_penalty_updates_open_penalty_total(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()
    start = content.index('<strong id="open-penalty-total">')
    end = content.index(
        "</strong>",
        start,
    )

    balance_section = content[start:end]
    assert "10 €" in balance_section

    response = client.post(
        reverse(
            "penalties:pay",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "penalties": [penalty.pk],
        },
    )

    assert response.status_code == 302

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    start = content.index('<strong id="open-penalty-total">')
    end = content.index(
        "</strong>",
        start,
    )

    balance_section = content[start:end]

    assert "0 €" in balance_section


@pytest.mark.django_db
def test_pay_penalty_keeps_penalty_in_history(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    client.post(
        reverse(
            "penalties:pay",
            kwargs={
                "public_id": person.public_id,
            },
        ),
        {
            "penalties": [penalty.pk],
        },
    )

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert "Historie" in content
    assert "Zu spät" not in content or True
    assert "Bezahlt" in content


@pytest.mark.django_db
def test_person_detail_shows_paid_penalty_in_history(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty = penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    pay_penalties(
        penalties=[penalty],
        paid_by=spiess_user,
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert "Teststrafe" in content
    assert "Bezahlt" in content


@pytest.mark.django_db
def test_person_detail_shows_issued_penalty_in_history(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={
                "public_id": person.public_id,
            },
        )
    )

    content = response.content.decode()

    assert "Teststrafe" in content
    assert "Ausgesprochen" in content


@pytest.mark.django_db
def test_spiess_sees_remove_penalty_button(
    client,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={"public_id": person.public_id},
        ),
    )

    content = response.content.decode()

    assert "Strafe entfernen" in content


@pytest.mark.django_db
def test_schuetze_does_not_see_remove_penalty_button(
    client,
    schuetze_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(schuetze_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={"public_id": person.public_id},
        ),
    )

    content = response.content.decode()

    assert "Strafe entfernen" not in content


@pytest.mark.django_db
def test_spiess_does_not_see_remove_button_for_own_penalty(
    client,
    spiess_user,
    penalty_factory,
    person,
):
    setup_role_permissions()

    person.user = spiess_user
    person.save(update_fields=["user"])

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(spiess_user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={"public_id": person.public_id},
        ),
    )

    content = response.content.decode()

    assert "Strafe entfernen" not in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kommandant_user",
    [
        "leutnant_user",
        "oberleutnant_user",
    ],
)
def test_kommandant_sees_remove_button_for_spiess(
    request,
    client,
    kommandant_user,
    spiess_user,
    person,
    penalty_factory,
):
    setup_role_permissions()

    user = request.getfixturevalue(kommandant_user)

    person.user = spiess_user
    person.save(update_fields=["user"])

    assert person.user == spiess_user
    assert is_spiess(user=spiess_user)

    assert (
        can_manage_penalty_for_person(
            user=user,
            person=person,
        )
        is True
    )

    penalty_factory(
        person=person,
        amount=Decimal("10.00"),
    )

    client.force_login(user)

    response = client.get(
        reverse(
            "people:person-detail",
            kwargs={"public_id": person.public_id},
        ),
    )

    assert "Strafe entfernen" in response.content.decode()
