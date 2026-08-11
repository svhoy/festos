from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from accounts.roles import ROLE_LABELS, Role

User = get_user_model()


def assign_role(*, user, role: Role) -> None:
    group, _ = Group.objects.get_or_create(
        name=ROLE_LABELS[role],
    )

    user.groups.clear()
    user.groups.add(group)


def get_role(
    *,
    user: User,
) -> Role | None:
    role_by_label = {label: role for role, label in ROLE_LABELS.items()}

    group = user.groups.first()

    if group is None:
        return None

    return role_by_label.get(group.name)
