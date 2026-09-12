from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from core.models import Doctor, Department, Patient
from .models import Referral


# ═══════════════════════════════════════════════════════════
# ثبت بیمار + ارجاع همزمان
# ═══════════════════════════════════════════════════════════
class PatientReferralSerializer(serializers.Serializer):
    """
    ثبت بیمار و ارجاع همزمان.

    - اگر بیمار با کد ملی وجود داشت → فقط ارجاع ثبت می‌شود
    - اگر بیمار وجود نداشت → هم بیمار و هم ارجاع ثبت می‌شوند
    """

    # ─────────── فیلدهای بیمار ───────────
    national_id = serializers.CharField(
        required=True,
        max_length=10,
        min_length=10,
        error_messages={
            'max_length': 'کد ملی باید ۱۰ رقم باشد',
            'min_length': 'کد ملی باید ۱۰ رقم باشد',
        },
    )
    full_name = serializers.CharField(required=True, max_length=150)
    phone = serializers.CharField(
        required=False, max_length=15, allow_blank=True, default=''
    )
    gender = serializers.ChoiceField(
        choices=[("male", "مرد"), ("female", "زن")],
        required=True,
    )
    birth_date = serializers.DateField(required=False, allow_null=True)

    # ─────────── فیلدهای ارجاع ───────────
    doctor_id = serializers.IntegerField(required=True)
    department_code = serializers.CharField(required=True, max_length=20)
    description = serializers.CharField(
        required=False, allow_blank=True, default=''
    )

    referral_date = serializers.DateTimeField(required=False)
    expiry_date = serializers.DateTimeField(required=False)

    # ─────────── اعتبارسنجی فیلدها ───────────
    def validate_national_id(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("کد ملی باید فقط شامل اعداد باشد")
        if len(value) != 10:
            raise serializers.ValidationError("کد ملی باید ۱۰ رقمی باشد")
        return value

    def validate_doctor_id(self, value):
        if not Doctor.objects.filter(id=value).exists():
            raise serializers.ValidationError("پزشک مورد نظر یافت نشد")
        return value

    def validate_department_code(self, value):
        if not Department.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(
                "بخش مورد نظر یافت نشد یا غیرفعال است"
            )
        return value

    def validate(self, data):
        referral_date = data.get('referral_date') or timezone.now()
        expiry_date = data.get('expiry_date') or (referral_date + timedelta(days=30))

        if expiry_date <= referral_date:
            raise serializers.ValidationError({
                'expiry_date': 'تاریخ انقضا باید بعد از تاریخ ارجاع باشد'
            })

        data['referral_date'] = referral_date
        data['expiry_date'] = expiry_date
        return data


# ═══════════════════════════════════════════════════════════
# نمایش ارجاع (برای لیست‌ها)
# ═══════════════════════════════════════════════════════════
class ReferralSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_national_id = serializers.CharField(source='patient.national_id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Referral
        fields = [
            'id', 'patient', 'patient_name', 'patient_national_id',
            'doctor', 'doctor_name', 'department', 'department_name',
            'referral_date', 'expiry_date', 'description',
            'status', 'status_display',
        ]
        read_only_fields = ['id', 'referral_date']

    def get_doctor_name(self, obj):
        if obj.doctor and obj.doctor.user:
            return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}".strip()
        return None