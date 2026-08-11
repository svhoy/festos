from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import can_manage_penalty_for_person, is_spiess
from penalties.queries import (
    get_active_catalog_entries,
    get_open_penalties,
    get_open_penalty_total,
    get_penalty_history,
)
from people.forms import PersonForm
from people.models import MembershipStatus, Person
from people.services import change_membership_status, create_person


@login_required
def person_list(request):
    people = Person.objects.all()

    return render(
        request,
        "people/person_list.html",
        {
            "people": people,
        },
    )


@login_required
def person_detail(request, public_id):
    person = get_object_or_404(
        Person,
        public_id=public_id,
    )

    context = {
        "person": person,
        "open_penalties": get_open_penalties(
            person=person,
        ),
        "open_penalty_total": get_open_penalty_total(
            person=person,
        ),
        "penalty_history": get_penalty_history(
            person=person,
        ),
        "catalog_entries": get_active_catalog_entries(),
        "can_manage_penalties": can_manage_penalty_for_person(
            user=request.user,
            person=person,
        ),
        "can_pay_penalties": is_spiess(
            user=request.user,
        ),
    }

    return render(
        request,
        "people/person_detail.html",
        context,
    )


def person_create(request):
    if request.method == "POST":
        form = PersonForm(request.POST)

        if form.is_valid():
            create_person(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                membership_status=form.cleaned_data["membership_status"],
            )

            return redirect("people:list")

    else:
        form = PersonForm()

    return render(
        request,
        "people/person_form.html",
        {
            "form": form,
        },
    )


def person_change_status(request, public_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    person = get_object_or_404(
        Person,
        public_id=public_id,
    )

    status = request.POST.get("membership_status")

    valid_statuses = {choice.value for choice in MembershipStatus}

    if status not in valid_statuses:
        return render(
            request,
            "people/person_detail.html",
            {
                "person": person,
                "status_error": "Ungültiger Mitgliedsstatus.",
            },
            status=400,
        )

    change_membership_status(
        person=person,
        status=MembershipStatus(status),
    )

    return redirect(
        "people:person-detail",
        public_id=person.public_id,
    )
