from django.conf import settings
from django.db import models


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )

    medical_code = models.CharField(
        max_length=20,
        unique=True
    )

    specialty = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Patient(models.Model):
    national_id = models.CharField(
        max_length=10,
        unique=True
    )

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "مرد"),
            ("female", "زن"),
        ]
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name

class Department(models.Model):

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name

class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=50
    )

    entity_type = models.CharField(
        max_length=50
    )

    entity_id = models.PositiveIntegerField()

    description = models.TextField(
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.action} - {self.entity_type}"