import pytest

from people.models import Person
from people.queries import get_person_by_public_id


@pytest.mark.django_db
def test_get_person_by_public_id(person):
    result = get_person_by_public_id(
        public_id=person.public_id,
    )

    assert result == person


@pytest.mark.django_db
def test_get_person_by_public_id_raises_for_unknown_id():
    with pytest.raises(Person.DoesNotExist):
        get_person_by_public_id(
            public_id="00000000-0000-0000-0000-000000000000",
        )
