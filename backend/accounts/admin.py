from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "phone",
        "is_active",
        "created_at",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        ("اطلاعات ورود", {
            "fields": (
                "username",
                "password",
            )
        }),
        ("اطلاعات شخصی", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "phone",
            )
        }),
        ("نقش کاربر", {
            "fields": (
                "role",
            )
        }),
        ("دسترسی‌ها", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("اطلاعات زمانی", {
            "fields": (
                "last_login",
                "date_joined",
                "created_at",
            )
        }),
    )

    add_fieldsets = (
        ("ایجاد کاربر جدید", {
            "classes": (
                "wide",
            ),
            "fields": (
                "username",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "email",
                "phone",
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )