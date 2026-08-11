from django.db.models import QuerySet

from people.models import Person


def get_person_by_public_id(
    *,
    public_id,
) -> Person:
    return Person.objects.get(
        public_id=public_id,
    )
