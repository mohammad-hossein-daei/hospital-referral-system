from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    _('نام کاربری یا رمز عبور اشتباه است'),
                    code='authorization'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    _('حساب کاربری شما غیرفعال است'),
                    code='authorization'
                )

            # بررسی نقش کاربر
            if user.role not in [User.Role.ADMIN, User.Role.RECEPTION, 
                                User.Role.DOCTOR, User.Role.MANAGER]:
                raise serializers.ValidationError(
                    _('شما دسترسی به سیستم ندارید'),
                    code='authorization'
                )

        else:
            raise serializers.ValidationError(
                _('نام کاربری و رمز عبور الزامی است'),
                code='authorization'
            )

        data['user'] = user
        return data

    def to_representation(self, instance):
        # این متد برای پاسخ نهایی استفاده می‌شود
        return {
            'user': {
                'id': instance.id,
                'username': instance.username,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'role': instance.role,
                'role_display': instance.get_role_display(),
                'phone': instance.phone,
            },
            'redirect_url': self.get_redirect_url(instance.role),
            'dashboard_type': self.get_dashboard_type(instance.role)
        }

    def get_redirect_url(self, role):
        """تعیین مسیر هدایت بر اساس نقش"""
        redirect_urls = {
            User.Role.ADMIN: '/admin/dashboard/',
            User.Role.RECEPTION: '/reception/dashboard/',
            User.Role.DOCTOR: '/doctor/dashboard/',
            User.Role.MANAGER: '/manager/dashboard/',
        }
        return redirect_urls.get(role, '/')

    def get_dashboard_type(self, role):
        """تعیین نوع داشبورد بر اساس نقش"""
        dashboard_types = {
            User.Role.ADMIN: 'admin',
            User.Role.RECEPTION: 'reception',
            User.Role.DOCTOR: 'doctor',
            User.Role.MANAGER: 'manager',
        }
        return dashboard_types.get(role, 'unknown')


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    # اضافه کردن اطلاعات پزشک
    doctor_info = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'email', 'phone', 'role', 'role_display',
            'is_active', 'last_login', 'created_at',
            'doctor_info',  # ← این رو اضافه کردم
        ]
        read_only_fields = ['last_login', 'created_at']
    
    def get_doctor_info(self, obj):
        """اگر کاربر پزشک باشه، اطلاعات پزشکی رو برمیگردونه"""
        if obj.role == User.Role.DOCTOR and hasattr(obj, 'doctor_profile'):
            return {
                'medical_code': obj.doctor_profile.medical_code,
                'specialty': obj.doctor_profile.specialty,
                'phone': obj.doctor_profile.phone,
            }
        return None