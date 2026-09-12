from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model

from .serializers import LoginSerializer, UserSerializer


User = get_user_model()


# ═══════════════════════════════════════════════════════════
# Mixin: منطق مشترک redirect و dashboard_type
# ═══════════════════════════════════════════════════════════
class RoleRedirectMixin:
    """
    منطق مشترک برای تعیین مسیر هدایت و نوع داشبورد
    بر اساس نقش و وضعیت سوپرادمین
    """

    def get_redirect_url(self, user):
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


# ═══════════════════════════════════════════════════════════
# Login
# ═══════════════════════════════════════════════════════════
class LoginView(RoleRedirectMixin, APIView):
    """
    ویو ورود کاربران با نقش‌های مختلف
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # لاگین کاربر
            login(request, user)

            response_data = {
                'success': True,
                'message': 'ورود با موفقیت انجام شد',

                'user': {
                    'id': user.id,
                    'national_code': user.national_code,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role,
                    'role_display': user.get_role_display(),
                    'phone': user.phone,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff,
                },

                'redirect_url': self.get_redirect_url(user),
                'dashboard_type': self.get_dashboard_type(user),
                'csrf_token': get_token(request),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════
# Logout
# ═══════════════════════════════════════════════════════════
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'کاربر وارد نشده است'
            }, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        return Response({
            'success': True,
            'message': 'خروج با موفقیت انجام شد'
        }, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════
# Current User
# ═══════════════════════════════════════════════════════════
class CurrentUserView(RoleRedirectMixin, APIView):
    """
    دریافت اطلاعات کاربر فعلی
    """

    def get(self, request):
        user = request.user

        if user.is_authenticated:
            serializer = UserSerializer(user)
            data = serializer.data

            data['dashboard_type'] = self.get_dashboard_type(user)
            data['redirect_url'] = self.get_redirect_url(user)
            data['is_superuser'] = user.is_superuser
            data['is_staff'] = user.is_staff

            return Response({
                'success': True,
                'data': data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'کاربر وارد نشده است'
        }, status=status.HTTP_401_UNAUTHORIZED)


# ═══════════════════════════════════════════════════════════
# Check Auth
# ═══════════════════════════════════════════════════════════
class CheckAuthView(RoleRedirectMixin, APIView):
    """
    بررسی وضعیت احراز هویت کاربر
    """
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'is_authenticated': True,
                'role': request.user.role,
                'username': request.user.username,
                'national_code': request.user.national_code,
                'is_superuser': request.user.is_superuser,
                'dashboard_type': self.get_dashboard_type(request.user),
                'redirect_url': self.get_redirect_url(request.user),
            }, status=status.HTTP_200_OK)

        return Response({
            'is_authenticated': False
        }, status=status.HTTP_200_OK)