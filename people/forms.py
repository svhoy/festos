from django import forms

from people.models import Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            "membership_status",
        )
