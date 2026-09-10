from django.conf import settings
from django.db import models


class Referral(models.Model):

    class Status(models.TextChoices):
        REGISTERED = "registered", "ثبت شده"
        USED = "used", "استفاده شده"
        CANCELLED = "cancelled", "لغو شده"
        EXPIRED = "expired", "منقضی شده"

    patient = models.ForeignKey(
        "core.Patient",
        on_delete=models.PROTECT,
        related_name="referrals"
    )

    doctor = models.ForeignKey(
        "core.Doctor",
        on_delete=models.PROTECT,
        related_name="referrals"
    )

    department = models.ForeignKey(
        "core.Department",
        on_delete=models.PROTECT,
        related_name="referrals"
    )

    referral_date = models.DateTimeField()

    expiry_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED
    )

    description = models.TextField(
        blank=True
    )

    reception_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="processed_referrals"
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.patient.full_name} - {self.department.name}"