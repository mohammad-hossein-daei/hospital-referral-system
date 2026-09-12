from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    national_code = serializers.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'کد ملی باید ۱۰ رقم عددی باشد')]
    )
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        national_code = data.get('national_code')
        password = data.get('password')

        if national_code and password:
            user = authenticate(
                request=self.context.get('request'),
                national_code=national_code,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    _('کد ملی یا رمز عبور اشتباه است'),
                    code='authorization'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    _('حساب کاربری شما غیرفعال است'),
                    code='authorization'
                )

            if user.role not in [
                User.Role.ADMIN,
                User.Role.RECEPTION,
                User.Role.DOCTOR,
                User.Role.MANAGER,
            ]:
                raise serializers.ValidationError(
                    _('شما دسترسی به سیستم ندارید'),
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                _('کد ملی و رمز عبور الزامی است'),
                code='authorization'
            )

        data['user'] = user
        return data

    def to_representation(self, instance):
        return {
            'user': {
                'id': instance.id,
                'national_code': instance.national_code,
                'username': instance.username,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'role': instance.role,
                'role_display': instance.get_role_display(),
                'phone': instance.phone,
                'is_superuser': instance.is_superuser,       # ← اضافه شد
                'is_staff': instance.is_staff,               # ← اضافه شد
            },
            'redirect_url': self.get_redirect_url(instance),
            'dashboard_type': self.get_dashboard_type(instance),
        }

    def get_redirect_url(self, user):
        """
        تعیین مسیر هدایت بر اساس نقش و وضعیت سوپرادمین
        """
        # سوپرادمین → ادمین جنگو
        if user.is_superuser:
            return '/admin/'

        redirect_urls = {
            User.Role.ADMIN: '/admin/dashboard/',
            User.Role.RECEPTION: '/reception/dashboard/',
            User.Role.DOCTOR: '/doctor/dashboard/',
            User.Role.MANAGER: '/manager/dashboard/',
        }
        return redirect_urls.get(user.role, '/')

    def get_dashboard_type(self, user):
        """
        تعیین نوع داشبورد بر اساس نقش و وضعیت سوپرادمین
        """
        # سوپرادمین → ادمین جنگو
        if user.is_superuser:
            return 'django-admin'

        dashboard_types = {
            User.Role.ADMIN: 'admin',
            User.Role.RECEPTION: 'reception',
            User.Role.DOCTOR: 'doctor',
            User.Role.MANAGER: 'manager',
        }
        return dashboard_types.get(user.role, 'unknown')


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    doctor_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'national_code', 'first_name', 'last_name',
            'email', 'phone', 'role', 'role_display',
            'is_active', 'last_login', 'created_at',
            'doctor_info',
        ]
        read_only_fields = ['last_login', 'created_at']

    def get_doctor_info(self, obj):
        if obj.role == User.Role.DOCTOR and hasattr(obj, 'doctor_profile'):
            return {
                'medical_code': obj.doctor_profile.medical_code,
                'specialty': obj.doctor_profile.specialty,
                'phone': obj.doctor_profile.phone,
            }
        return None