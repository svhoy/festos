from django.contrib import admin

from people.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "membership_status",
        "created_at",
    )

    list_filter = ("membership_status",)

    search_fields = (
        "first_name",
        "last_name",
        "public_id",
    )

    readonly_fields = (
        "public_id",
        "created_at",
        "updated_at",
    )
