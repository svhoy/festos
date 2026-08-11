from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from accounts.roles import Role
from accounts.services import assign_role
from penalties.models import Penalty, PenaltyCatalogEntry
from people.models import Person

User = get_user_model()


@pytest.fixture
def person(db):
    return Person.objects.create(
        first_name="Max",
        last_name="Mustermann",
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="test-user",
        password="test-password",
    )


@pytest.fixture
def catalog_entry(db):
    return PenaltyCatalogEntry.objects.create(
        name="Zu spät zum Antreten",
        amount=Decimal("5.00"),
    )


@pytest.fixture
def other_person(db):
    return Person.objects.create(
        first_name="Anna",
        last_name="Mustermann",
    )


@pytest.fixture
def penalty(penalty_factory):
    return penalty_factory()


@pytest.fixture
def penalty_factory(db, person, user):
    def create_penalty(
        *,
        person=person,
        amount=Decimal("10.00"),
        issued_by=user,
        catalog_entry=None,
        removed_at=None,
        removed_by=None,
    ):
        if catalog_entry is None:
            catalog_entry = PenaltyCatalogEntry.objects.create(
                name="Teststrafe",
                description="Test-Strafenkatalogeintrag",
                amount=amount,
            )

        return Penalty.objects.create(
            person=person,
            catalog_entry=catalog_entry,
            amount=amount,
            issued_by=issued_by,
            removed_at=removed_at,
            removed_by=removed_by,
        )

    return create_penalty


@pytest.fixture
def spiess_user(db):
    user = User.objects.create_user(
        username="spiess-user",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SPIESS,
    )

    return user


@pytest.fixture
def schuetze_user(db):
    user = User.objects.create_user(
        username="schuetze-user",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.SCHUETZE,
    )

    return user


@pytest.fixture
def penalty_catalog_entry_factory(db):
    def create_catalog_entry(**kwargs):
        defaults = {
            "name": "Teststrafe",
            "description": "Testbeschreibung",
            "amount": Decimal("10.00"),
            "is_active": True,
        }

        defaults.update(kwargs)

        return PenaltyCatalogEntry.objects.create(
            **defaults,
        )

    return create_catalog_entry


@pytest.fixture
def oberleutnant_user(db):
    user = User.objects.create_user(
        username="oberleutnant-user",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.OBERLEUTNANT,
    )

    return user


@pytest.fixture
def leutnant_user(db):
    user = User.objects.create_user(
        username="leutnant-user",
        password="test-password",
    )

    assign_role(
        user=user,
        role=Role.LEUTNANT,
    )

    return user


@pytest.fixture
def spiess_person(spiess_user):
    return Person.objects.create(
        first_name="Max",
        last_name="Spieß",
        user=spiess_user,
    )
