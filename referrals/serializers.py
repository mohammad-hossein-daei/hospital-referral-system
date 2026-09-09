from core.models import Doctor, Department
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

# ما اینجا کلاس serializer رو می‌سازیم
# serializer یعنی داده‌هایی که از API می‌گیریم رو بررسی و اعتبارسنجی می‌کنه
class PatientReferralSerializer(serializers.Serializer):
    """
    این کلاس مشخص می‌کنه که وقتی کاربر یک درخواست به API می‌فرسته،
    چه فیلدهایی باید داشته باشه و هر کدوم چه نوع داده‌ای هستن
    """
    
    # ---------- فیلدهای بیمار ----------
    # required=True یعنی حتماً باید این فیلد رو کاربر بفرسته
    national_id = serializers.CharField(required=True, max_length=10)
    full_name = serializers.CharField(required=True, max_length=150)
    
    # required=False یعنی اگه نفرستاد، مشکلی نیست
    phone = serializers.CharField(required=False, max_length=15, allow_blank=True)
    
    # choice یعنی فقط یکی از این دو مقدار رو می‌تونه داشته باشه
    gender = serializers.ChoiceField(
        choices=[("male", "مرد"), ("female", "زن")], 
        required=True
    )
    
    # allow_null=True یعنی می‌تونه خالی باشه یا null باشه
    birth_date = serializers.DateField(required=False, allow_null=True)
    
    # ---------- فیلدهای ارجاع ----------
    doctor_id = serializers.IntegerField(required=True)
    department_code = serializers.CharField(required=True, max_length=20)
    description = serializers.CharField(required=False, allow_blank=True)


class PatientReferralSerializer(serializers.Serializer):
    # فیلدهای بیمار
    national_id = serializers.CharField(required=True, max_length=10)
    full_name = serializers.CharField(required=True, max_length=150)
    phone = serializers.CharField(required=False, max_length=15, allow_blank=True)
    gender = serializers.ChoiceField(
        choices=[("male", "مرد"), ("female", "زن")],
        required=True
    )
    birth_date = serializers.DateField(required=False, allow_null=True)
    
    # فیلدهای ارجاع
    doctor_id = serializers.IntegerField(required=True)
    department_code = serializers.CharField(required=True, max_length=20)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_national_id(self, value):
        """بررسی کد ملی: باید ۱۰ رقم باشد"""
        if not value.isdigit():
            raise serializers.ValidationError("کد ملی باید فقط شامل اعداد باشد")
        if len(value) != 10:
            raise serializers.ValidationError("کد ملی باید ۱۰ رقمی باشد")
        return value
    
    def validate_doctor_id(self, value):
        """بررسی اینکه دکتر وجود دارد"""
        if not Doctor.objects.filter(id=value).exists():
            raise serializers.ValidationError("پزشک مورد نظر یافت نشد")
        return value
    
    def validate_department_code(self, value):
        """بررسی اینکه بخش وجود دارد و فعال است"""
        from core.models import Department
        if not Department.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("بخش مورد نظر یافت نشد یا غیرفعال است")
        return value
    
    def validate(self, data):
        """اضافه کردن تاریخ‌های ارجاع به صورت خودکار"""
        data['referral_date'] = timezone.now()
        data['expiry_date'] = timezone.now() + timedelta(days=30)
        return data