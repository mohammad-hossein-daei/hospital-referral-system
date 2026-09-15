from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from core.models import Doctor
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
                'is_superuser': instance.is_superuser,
                'is_staff': instance.is_staff,
            },
            'redirect_url': self.get_redirect_url(instance),
            'dashboard_type': self.get_dashboard_type(instance),
        }

    def get_redirect_url(self, user):
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

class AdminUserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'national_code', 'first_name', 'last_name',
            'email', 'phone', 'role', 'role_display',
            'is_active', 'is_staff', 'is_superuser',
            'last_login', 'created_at',
        ]
        read_only_fields = ['last_login', 'created_at']


class AdminUserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'national_code', 'first_name', 'last_name',
            'email', 'phone', 'role', 'password', 'is_active',
        ]

    def validate_password(self, value):
        if not self.instance and not value:
            raise serializers.ValidationError('رمز عبور برای ایجاد کاربر الزامی است')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class DoctorSerializer(serializers.ModelSerializer):
    user = AdminUserCreateUpdateSerializer()

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'medical_code', 'specialty', 'phone']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = User.Role.DOCTOR
        user_serializer = AdminUserCreateUpdateSerializer()
        user = user_serializer.create(user_data)
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = AdminUserCreateUpdateSerializer()
            user_serializer.update(instance.user, user_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ReceptionistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'national_code', 'first_name', 'last_name',
            'email', 'phone', 'password', 'is_active',
        ]
        extra_kwargs = {'password': {'write_only': True, 'required': False, 'min_length': 8}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = User.Role.RECEPTION
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance