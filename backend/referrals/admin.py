from django.contrib import admin

from .forms import DoctorAdminForm
from .models import Doctor, Patient, Department, AuditLog


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm

    list_display = (
        "get_full_name",
        "medical_code",
        "specialty",
        "phone",
    )

    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__username",
        "medical_code",
        "specialty",
        "phone",
    )

    list_filter = (
        "specialty",
    )

    ordering = (
        "user__last_name",
        "user__first_name",
    )

    list_select_related = (
        "user",
    )

    @admin.display(description="نام پزشک", ordering="user__last_name")
    def get_full_name(self, obj):
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()

        if full_name:
            return full_name

        return obj.user.username


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "national_id",
        "phone",
        "gender",
        "birth_date",
        "created_at",
    )

    search_fields = (
        "full_name",
        "national_id",
        "phone",
    )

    list_filter = (
        "gender",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "name",
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "entity_type",
        "entity_id",
        "ip_address",
        "created_at",
    )

    list_select_related = (
        "user",
    )

    search_fields = (
        "user__username",
        "action",
        "entity_type",
        "description",
        "ip_address",
    )

    list_filter = (
        "action",
        "entity_type",
        "created_at",
    )

    ordering = (
        "-created_at",
    )