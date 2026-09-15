from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAdminRole

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import login, logout
#from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from core.models import Doctor

from .serializers import (
    LoginSerializer, 
    UserSerializer,
    AdminUserListSerializer,
    AdminUserCreateUpdateSerializer,
    DoctorSerializer,
    ReceptionistSerializer,
)


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
        # سوپریوزر واقعی جنگو (Developer/System) → ادمین جنگو
        if user.is_superuser and user.is_staff:
            return '/admin/'

        # سوپریوزر React Admin (is_staff=False) یا بقیه نقش‌ها
        redirect_urls = {
            User.Role.ADMIN: '/admin/dashboard/',
            User.Role.RECEPTION: '/reception/dashboard/',
            User.Role.DOCTOR: '/doctor/dashboard/',
            User.Role.MANAGER: '/manager/dashboard/',
        }
        return redirect_urls.get(user.role, '/')

    def get_dashboard_type(self, user):
        # سوپریوزر واقعی جنگو (Developer/System) → ادمین جنگو
        if user.is_superuser and user.is_staff:
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

            # ساخت توکن‌های JWT به‌جای session
            refresh = RefreshToken.for_user(user)

            response_data = {
                'success': True,
                'message': 'ورود با موفقیت انجام شد',

                'access': str(refresh.access_token),
                'refresh': str(refresh),

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
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({
                'success': False,
                'message': 'توکن refresh ارسال نشده است'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({
                'success': False,
                'message': 'توکن نامعتبر است'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'message': 'خروج با موفقیت انجام شد'
        }, status=status.HTTP_200_OK)

# ═══════════════════════════════════════════════════════════
# Current User
# ═══════════════════════════════════════════════════════════
class CurrentUserView(RoleRedirectMixin, APIView):
    def get(self, request):
        user = request.user
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

# ═══════════════════════════════════════════════════════════
# Check Auth
# ═══════════════════════════════════════════════════════════
class CheckAuthView(RoleRedirectMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'is_authenticated': True,
            'role': request.user.role,
            'username': request.user.username,
            'national_code': request.user.national_code,
            'is_superuser': request.user.is_superuser,
            'dashboard_type': self.get_dashboard_type(request.user),
            'redirect_url': self.get_redirect_url(request.user),
        }, status=status.HTTP_200_OK)

# ═══════════════════════════════════════════════════════════
# Admin: Users
# ═══════════════════════════════════════════════════════════
class AdminUserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateUpdateSerializer
        return AdminUserListSerializer


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.all()
    serializer_class = AdminUserCreateUpdateSerializer


class AdminUserToggleActiveView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return Response({
            'success': True,
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════
# Admin: Doctors
# ═══════════════════════════════════════════════════════════
class AdminDoctorListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class AdminDoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


# ═══════════════════════════════════════════════════════════
# Admin: Receptionists
# ═══════════════════════════════════════════════════════════
class AdminReceptionistListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.filter(role=User.Role.RECEPTION)
    serializer_class = ReceptionistSerializer


class AdminReceptionistDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.filter(role=User.Role.RECEPTION)
    serializer_class = ReceptionistSerializer