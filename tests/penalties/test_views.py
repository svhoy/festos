from decimal import Decimal

import pytest
from django.urls import reverse

from accounts.role_permissions import setup_role_permissions
from penalties.models import Payment, Penalty, PenaltyCatalogEntry, PenaltyEvent


@pytest.mark.django_db
def test_spiess_can_issue_penalty(
    client,
    spiess_user,
    person,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()
    catalog_entry = penalty_catalog_entry_factory(
        amount=Decimal("15.00"),
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

    penalty = Penalty.objects.get(
        person=person,
    )

    assert penalty.catalog_entry == catalog_entry
    assert penalty.amount == Decimal("15.00")
    assert penalty.issued_by == spiess_user

    assert PenaltyEvent.objects.filter(
        penalty=penalty,
        event_type=PenaltyEvent.EventType.ISSUED,
        created_by=spiess_user,
    ).exists()


@pytest.mark.django_db
def test_schuetze_cannot_issue_penalty(
    client,
    schuetze_user,
    person,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()
    catalog_entry = penalty_catalog_entry_factory()

    client.force_login(schuetze_user)

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

    assert response.status_code == 403

    assert not Penalty.objects.filter(
        person=person,
    ).exists()


@pytest.mark.django_db
def test_spiess_can_access_catalog(
    client,
    spiess_user,
):
    setup_role_permissions()

    client.force_login(spiess_user)

    response = client.get(
        reverse("penalties:catalog-list"),
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_schuetze_cannot_access_catalog(
    client,
    schuetze_user,
):
    setup_role_permissions()

    client.force_login(schuetze_user)

    response = client.get(
        reverse("penalties:catalog-list"),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_spiess_can_create_catalog_entry(
    client,
    spiess_user,
):
    setup_role_permissions()

    client.force_login(spiess_user)

    response = client.post(
        reverse("penalties:catalog-create"),
        {
            "name": "Zu spät",
            "description": "Verspätetes Erscheinen",
            "amount": "10.00",
        },
    )

    assert response.status_code == 302

    entry = PenaltyCatalogEntry.objects.get(
        name="Zu spät",
    )

    assert entry.amount == Decimal("10.00")


@pytest.mark.django_db
def test_spiess_can_deactivate_catalog_entry(
    client,
    spiess_user,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()

    entry = penalty_catalog_entry_factory(
        is_active=True,
    )

    client.force_login(spiess_user)

    response = client.post(
        reverse(
            "penalties:catalog-deactivate",
            kwargs={"pk": entry.pk},
        ),
    )

    assert response.status_code == 302

    entry.refresh_from_db()

    assert entry.is_active is False


@pytest.mark.django_db
def test_spiess_can_activate_catalog_entry(
    client,
    spiess_user,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()

    entry = penalty_catalog_entry_factory(
        is_active=False,
    )

    client.force_login(spiess_user)

    response = client.post(
        reverse(
            "penalties:catalog-activate",
            kwargs={"pk": entry.pk},
        ),
    )

    assert response.status_code == 302

    entry.refresh_from_db()

    assert entry.is_active is True


@pytest.mark.django_db
def test_schuetze_cannot_deactivate_catalog_entry(
    client,
    schuetze_user,
    penalty_catalog_entry_factory,
):
    setup_role_permissions()

    entry = penalty_catalog_entry_factory(
        is_active=True,
    )

    client.force_login(schuetze_user)

    response = client.post(
        reverse(
            "penalties:catalog-deactivate",
            kwargs={"pk": entry.pk},
        ),
    )

    assert response.status_code == 403

    entry.refresh_from_db()

    assert entry.is_active is True


@pytest.mark.django_db
def test_spiess_can_issue_penalty_for_person(
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
        data={
            "person": person.pk,
            "catalog_entry": catalog_entry.pk,
        },
    )

    assert response.status_code == 200

    penalty = Penalty.objects.get()

    assert penalty.person == person
    assert penalty.catalog_entry == catalog_entry
    assert penalty.amount == Decimal("10.00")
    assert penalty.issued_by == spiess_user


@pytest.mark.django_db
def test_pay_all_does_nothing_when_no_open_penalties(
    client,
    spiess_user,
    person,
):
    setup_role_permissions()

    client.force_login(spiess_user)

    response = client.post(
        reverse(
            "penalties:pay-all",
            kwargs={
                "public_id": person.public_id,
            },
        ),
    )

    assert response.status_code == 302
    assert Payment.objects.count() == 0


@pytest.mark.django_db
def test_spiess_can_remove_penalty(
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

    response = client.post(
        reverse(
            "penalties:remove",
            kwargs={"pk": penalty.pk},
        ),
    )

    assert response.status_code == 302

    penalty.refresh_from_db()

    assert penalty.removed_at is not None
    assert penalty.removed_by == spiess_user


@pytest.mark.django_db
def test_schuetze_cannot_remove_penalty(
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

    response = client.post(
        reverse(
            "penalties:remove",
            kwargs={"pk": penalty.pk},
        ),
    )

    assert response.status_code == 403

    penalty.refresh_from_db()

    assert penalty.removed_at is None


@pytest.mark.django_db
def test_remove_penalty_requires_post(
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
            "penalties:remove",
            kwargs={"pk": penalty.pk},
        ),
    )

    assert response.status_code == 405


@pytest.mark.django_db
def test_issue_penalty_htmx_updates_all_person_penalty_sections(
    client,
    spiess_user,
    person,
    catalog_entry,
):
    setup_role_permissions()

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
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200

    content = response.content.decode()

    assert 'id="penalty-balance"' in content
    assert 'id="penalty-yearly-summary"' in content
    assert 'id="penalty-area"' in content
    assert 'id="history-area"' in content

    assert 'hx-swap-oob="true"' in content
    assert "Zu spät zum Antreten" in content
    assert "Ausgesprochen" in content
    assert "5 " in content


@pytest.mark.django_db
def test_pay_penalty_htmx_updates_all_person_penalty_sections(
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
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200

    content = response.content.decode()

    assert 'id="penalty-balance"' in content
    assert 'id="penalty-yearly-summary"' in content
    assert 'id="penalty-area"' in content
    assert 'id="history-area"' in content

    assert 'hx-swap-oob="true"' in content

    assert "Bezahlt" in content
