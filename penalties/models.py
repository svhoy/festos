# Create your models here.
from django.conf import settings
from django.db import models

from people.models import Person


class PenaltyCatalogEntry(models.Model):
    name = models.CharField(
        max_length=200,
    )
    description = models.TextField(
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

        permissions = [
            (
                "manage_catalog",
                "Kann den Strafenkatalog verwalten",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Penalty(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="penalties",
    )

    catalog_entry = models.ForeignKey(
        PenaltyCatalogEntry,
        on_delete=models.PROTECT,
        related_name="penalties",
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_penalties",
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
    )
    removed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    removed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="removed_penalties",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def status(self) -> str:
        latest_status_event = (
            self.events.exclude(
                event_type=PenaltyEvent.EventType.AMOUNT_CHANGED,
            )
            .order_by("-created_at", "-pk")
            .first()
        )

        if latest_status_event is None:
            return PenaltyEvent.EventType.ISSUED

        return latest_status_event.event_type

    class Meta:
        ordering = ["-issued_at"]

        permissions = [
            (
                "issue_penalty",
                "Kann Strafen aussprechen",
            ),
            (
                "remove_penalty",
                "Kann Strafen löschen",
            ),
            (
                "mark_penalty_paid",
                "Kann Strafen als bezahlt markieren",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.person} – {self.catalog_entry}"


class Payment(models.Model):
    penalties = models.ManyToManyField(
        Penalty,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    paid_at = models.DateTimeField(
        auto_now_add=True,
    )

    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="penalty_payments",
    )

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self) -> str:
        return f"{self.amount:.2f} €"


class PenaltyEvent(models.Model):
    class EventType(models.TextChoices):
        ISSUED = "issued", "Ausgesprochen"
        PAID = "paid", "Bezahlt"
        REMOVED = "removed", "Entfernt"
        AMOUNT_CHANGED = "amount_changed", "Betrag geändert"

    penalty = models.ForeignKey(
        Penalty,
        on_delete=models.PROTECT,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="penalty_events",
    )
    previous_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    new_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]
