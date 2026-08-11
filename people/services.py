from django.contrib.auth import get_user_model

from people.models import MembershipStatus, Person

User = get_user_model()


def create_person(
    *,
    first_name: str,
    last_name: str,
    membership_status: MembershipStatus = (MembershipStatus.ACTIVE),
    user: User | None = None,
) -> Person:
    return Person.objects.create(
        first_name=first_name,
        last_name=last_name,
        membership_status=membership_status,
        user=user,
    )


def change_membership_status(
    *,
    person: Person,
    status: MembershipStatus,
) -> Person:
    if person.membership_status == status:
        return person

    person.membership_status = status
    person.save(
        update_fields=[
            "membership_status",
            "updated_at",
        ],
    )

    return person
