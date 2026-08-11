from django.contrib.auth.models import Group, Permission

from accounts.roles import ROLE_LABELS, Role

VIEW_PERSON = ("people", "view_person")
MANAGE_PERSON = ("people", "manage_person")

# VIEW_RANKING = ("ranking", "view_ranking")

VIEW_PENALTY = ("penalties", "view_penalty")
ISSUE_PENALTY = ("penalties", "issue_penalty")
REMOVE_PENALTY = ("penalties", "remove_penalty")
MARK_PENALTY_PAID = ("penalties", "mark_penalty_paid")
MANAGE_CATALOG = ("penalties", "manage_catalog")

# MANAGE_RFID = ("rfid", "manage_rfid")
# MANAGE_ROLES = ("accounts", "manage_roles")

ROLE_PERMISSIONS = {
    Role.ADMIN: {
        VIEW_PERSON,
        MANAGE_PERSON,
        MANAGE_CATALOG,
        # MANAGE_RFID,
        # MANAGE_ROLES,
        # VIEW_RANKING,
    },
    Role.SPIESS: {
        VIEW_PERSON,
        MANAGE_PERSON,
        VIEW_PENALTY,
        ISSUE_PENALTY,
        REMOVE_PENALTY,
        MARK_PENALTY_PAID,
        MANAGE_CATALOG,
        # MANAGE_RFID,
        # VIEW_RANKING,
    },
    Role.OBERLEUTNANT: {
        VIEW_PERSON,
        # VIEW_RANKING,
    },
    Role.LEUTNANT: {
        VIEW_PERSON,
        # VIEW_RANKING,
    },
    Role.SCHUETZE: {
        VIEW_PERSON,
        # VIEW_RANKING,
    },
}


def setup_role_permissions() -> None:
    for role, permissions in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(
            name=ROLE_LABELS[role],
        )

        group.permissions.clear()

        for app_label, codename in permissions:
            permission = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )

            group.permissions.add(permission)
