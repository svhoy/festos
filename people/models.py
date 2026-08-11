import uuid

from django.conf import settings
from django.db import models


class MembershipStatus(models.TextChoices):
    ACTIVE = "Aktiv"
    PASSIVE = "Passiv"
    LEFT = "Ausgetreten"


class Person(models.Model):
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    membership_status = models.CharField(
        max_length=20,
        choices=MembershipStatus,
        default=MembershipStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

        permissions = [
            (
                "manage_person",
                "Kann Personen verwalten",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
