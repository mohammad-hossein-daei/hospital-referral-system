from django.contrib import admin
from .models import Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'department', 'referral_date', 'status']
    list_filter = ['status', 'department']
    search_fields = ['patient__full_name', 'patient__national_id']
    readonly_fields = ['created_at', 'updated_at']