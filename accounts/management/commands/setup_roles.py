from django.core.management.base import BaseCommand

from accounts.role_permissions import (
    setup_role_permissions,
)


class Command(BaseCommand):
    help = "Richtet FESTOS-Rollen und Berechtigungen ein."

    def handle(self, *args, **options):
        setup_role_permissions()

        self.stdout.write(
            self.style.SUCCESS(
                "FESTOS-Rollen wurden eingerichtet.",
            ),
        )
