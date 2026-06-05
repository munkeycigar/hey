from django.contrib import admin

from .models import BusinessCard


@admin.register(BusinessCard)
class BusinessCardAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "email", "phone", "organization", "updated_at")
    list_filter = ("owner", "updated_at")
    search_fields = ("label", "first_name", "last_name", "email", "organization")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Card")
    def name(self, obj):
        return obj.full_label
