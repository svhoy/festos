from decimal import Decimal

import pytest

from penalties.models import PenaltyCatalogEntry
from penalties.services import (
    activate_catalog_entry,
    create_catalog_entry,
    deactivate_catalog_entry,
)


@pytest.mark.django_db
def test_create_catalog_entry():
    entry = create_catalog_entry(
        name="Zu spät",
        description="Zu spät zum Antreten",
        amount=Decimal("10.00"),
    )

    assert entry.name == "Zu spät"
    assert entry.description == "Zu spät zum Antreten"
    assert entry.amount == Decimal("10.00")
    assert entry.is_active is True


@pytest.mark.django_db
def test_deactivate_catalog_entry(catalog_entry):
    deactivate_catalog_entry(
        catalog_entry=catalog_entry,
    )

    catalog_entry.refresh_from_db()

    assert catalog_entry.is_active is False


@pytest.mark.django_db
def test_activate_catalog_entry(catalog_entry):
    catalog_entry.is_active = False
    catalog_entry.save()

    activate_catalog_entry(
        catalog_entry=catalog_entry,
    )

    catalog_entry.refresh_from_db()

    assert catalog_entry.is_active is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-1.00"),
    ],
)
def test_create_catalog_entry_rejects_invalid_amount(
    amount,
):
    with pytest.raises(ValueError):
        create_catalog_entry(
            name="Ungültige Strafe",
            amount=amount,
        )
