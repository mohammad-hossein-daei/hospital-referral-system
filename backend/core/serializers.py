from rest_framework import serializers
from django.core.validators import RegexValidator

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "national_id",
            "full_name",
            "phone",
            "gender",
            "birth_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "national_id": {
                "validators": [
                    RegexValidator(r'^\d{10}$', 'کد ملی بیمار باید ۱۰ رقم عددی باشد')
                ]
            }
        }    