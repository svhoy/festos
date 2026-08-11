from decimal import Decimal

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import can_manage_penalty_for_person, is_spiess
from penalties.models import Penalty, PenaltyCatalogEntry
from penalties.queries import get_open_penalties, get_open_penalty_total
from penalties.services import (
    activate_catalog_entry,
    create_catalog_entry,
    deactivate_catalog_entry,
    issue_penalty,
    pay_penalties,
    remove_penalty,
    update_catalog_entry,
)
from people.models import Person


@login_required
def catalog_list_view(
    request: HttpRequest,
) -> HttpResponse:
    if not request.user.has_perm("penalties.manage_catalog"):
        return HttpResponseForbidden()

    catalog_entries = PenaltyCatalogEntry.objects.all()

    return render(
        request,
        "penalties/catalog_list.html",
        {
            "catalog_entries": catalog_entries,
        },
    )


@login_required
def catalog_create_view(
    request: HttpRequest,
) -> HttpResponse:
    if not request.user.has_perm("penalties.manage_catalog"):
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(
            request,
            "penalties/catalog_form.html",
        )

    amount = Decimal(
        request.POST["amount"],
    )

    create_catalog_entry(
        name=request.POST["name"],
        description=request.POST.get("description", ""),
        amount=amount,
    )

    return redirect("penalties:catalog-list")


@login_required
def catalog_update_view(
    request: HttpRequest,
    pk: int,
) -> HttpResponse:
    if not request.user.has_perm("penalties.manage_catalog"):
        return HttpResponseForbidden()

    catalog_entry = get_object_or_404(
        PenaltyCatalogEntry,
        pk=pk,
    )

    if request.method == "GET":
        return render(
            request,
            "penalties/catalog_form.html",
            {
                "catalog_entry": catalog_entry,
            },
        )

    amount = Decimal(
        request.POST["amount"],
    )

    update_catalog_entry(
        catalog_entry=catalog_entry,
        name=request.POST["name"],
        description=request.POST.get("description", ""),
        amount=amount,
    )

    return redirect("penalties:catalog-list")


@login_required
@require_POST
def catalog_activate_view(
    request: HttpRequest,
    pk: int,
) -> HttpResponse:
    if not request.user.has_perm("penalties.manage_catalog"):
        return HttpResponseForbidden()

    catalog_entry = get_object_or_404(
        PenaltyCatalogEntry,
        pk=pk,
    )

    activate_catalog_entry(
        catalog_entry=catalog_entry,
    )

    return redirect("penalties:catalog-list")


@login_required
@require_POST
def catalog_deactivate_view(
    request: HttpRequest,
    pk: int,
) -> HttpResponse:
    if not request.user.has_perm("penalties.manage_catalog"):
        return HttpResponseForbidden()

    catalog_entry = get_object_or_404(
        PenaltyCatalogEntry,
        pk=pk,
    )

    deactivate_catalog_entry(
        catalog_entry=catalog_entry,
    )

    return redirect("penalties:catalog-list")


@login_required
def issue_penalty_view(
    request: HttpRequest,
    public_id,
) -> HttpResponse:

    if not request.user.has_perm("penalties.issue_penalty"):
        return HttpResponseForbidden()

    if request.method != "POST":
        return HttpResponse(status=405)

    person = get_object_or_404(
        Person,
        public_id=public_id,
    )

    catalog_entry = get_object_or_404(
        PenaltyCatalogEntry,
        pk=request.POST.get("catalog_entry"),
        is_active=True,
    )

    issue_penalty(
        person=person,
        catalog_entry=catalog_entry,
        issued_by=request.user,
    )

    return render(
        request,
        "people/partials/penalty_area.html",
        {
            "person": person,
            "open_penalties": get_open_penalties(
                person=person,
            ),
            "open_penalty_total": get_open_penalty_total(
                person=person,
            ),
        },
    )


@login_required
def remove_penalty_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    penalty = get_object_or_404(
        Penalty,
        pk=pk,
    )

    if not can_manage_penalty_for_person(
        user=request.user,
        person=penalty.person,
    ):
        return HttpResponseForbidden()

    remove_penalty(
        penalty=penalty,
        removed_by=request.user,
    )

    return redirect(
        "people:person-detail",
        public_id=penalty.person.public_id,
    )


@login_required
def pay_penalties_view(request, public_id):
    if not is_spiess(user=request.user):
        raise PermissionDenied

    person = get_object_or_404(
        Person,
        public_id=public_id,
    )

    if request.method != "POST":
        return redirect(
            "people:person-detail",
            public_id=person.public_id,
        )

    penalty_ids = request.POST.getlist("penalties")

    penalties = list(
        Penalty.objects.filter(
            pk__in=penalty_ids,
            person=person,
            removed_at__isnull=True,
        )
    )

    pay_penalties(
        penalties=penalties,
        paid_by=request.user,
    )

    return redirect(
        "people:person-detail",
        public_id=person.public_id,
    )


@login_required
@permission_required(
    "penalties.mark_penalty_paid",
    raise_exception=True,
)
def pay_all_penalties_view(request, public_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    person = get_object_or_404(
        Person,
        public_id=public_id,
    )

    penalties = list(
        get_open_penalties(
            person=person,
        )
    )

    if not penalties:
        return redirect(
            "people:person-detail",
            public_id=person.public_id,
        )

    pay_penalties(
        penalties=penalties,
        paid_by=request.user,
    )

    return redirect(
        "people:person-detail",
        public_id=person.public_id,
    )
