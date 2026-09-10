from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "مدیر سیستم"
        RECEPTION = "reception", "پذیرش"
        DOCTOR = "doctor", "پزشک"
        MANAGER = "manager", "مدیر بخش"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DOCTOR,
    )

    phone = models.CharField(
        max_length=11,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username