from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "مدیر سیستم"
        RECEPTION = "reception", "پذیرش"
        DOCTOR = "doctor", "پزشک"
        MANAGER = "manager", "مدیر بخش"

    national_code = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(r'^\d{10}$', 'کد ملی باید ۱۰ رقم عددی باشد')
        ],
        verbose_name="کد ملی",
    )

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

    USERNAME_FIELD = 'national_code'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # سوپرادمین همیشه role=admin
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} - {self.national_code}"