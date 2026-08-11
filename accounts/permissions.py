from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from accounts.roles import Role
from accounts.services import get_role
from people.models import Person

User = get_user_model()


def has_role(
    *,
    user: User,
    role: Role,
) -> bool:
    return get_role(user=user) == role


def is_spiess(
    *,
    user: User,
) -> bool:
    return has_role(
        user=user,
        role=Role.SPIESS,
    )


def is_admin(
    *,
    user: User,
) -> bool:
    return has_role(
        user=user,
        role=Role.ADMIN,
    )


def is_kommandant(
    *,
    user: User,
) -> bool:
    role = get_role(user=user)

    return role in {
        Role.OBERLEUTNANT,
        Role.LEUTNANT,
    }


def can_manage_penalty_for_person(
    *,
    user: User,
    person: Person,
) -> bool:
    if is_spiess(user=user):
        return person.user != user

    if is_kommandant(user=user):
        return person.user is not None and is_spiess(user=person.user)

    return False
