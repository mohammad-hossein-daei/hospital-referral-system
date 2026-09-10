from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model

from .serializers import LoginSerializer, UserSerializer


User = get_user_model()


class LoginView(APIView):
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
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role,
                    'role_display': user.get_role_display(),
                    'phone': user.phone,
                },

                'redirect_url': self.get_redirect_url(user.role),

                'dashboard_type': self.get_dashboard_type(user.role),

                'csrf_token': get_token(request)
            }

            return Response(
                response_data,
                status=status.HTTP_200_OK
            )

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get_redirect_url(self, role):
        """
        تعیین مسیر هدایت بر اساس نقش
        """

        redirect_urls = {
            User.Role.ADMIN: '/admin/dashboard/',
            User.Role.RECEPTION: '/reception/dashboard/',
            User.Role.DOCTOR: '/doctor/dashboard/',
            User.Role.MANAGER: '/manager/dashboard/',
        }

        return redirect_urls.get(role, '/')

    def get_dashboard_type(self, role):
        """
        تعیین نوع داشبورد بر اساس نقش
        """

        dashboard_types = {
            User.Role.ADMIN: 'admin',
            User.Role.RECEPTION: 'reception',
            User.Role.DOCTOR: 'doctor',
            User.Role.MANAGER: 'manager',
        }

        return dashboard_types.get(role, 'unknown')


class LogoutView(APIView):
    """
    API خروج کاربر از سیستم
    برای تمام نقش‌ها
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        logout(request)

        return Response({
            'success': True,
            'message': 'خروج با موفقیت انجام شد'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    دریافت اطلاعات کاربر فعلی
    """

    def get(self, request):

        user = request.user

        if user.is_authenticated:

            serializer = UserSerializer(user)

            data = serializer.data

            data['dashboard_type'] = self.get_dashboard_type(
                user.role
            )

            data['redirect_url'] = self.get_redirect_url(
                user.role
            )

            return Response({
                'success': True,
                'data': data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'کاربر وارد نشده است'
        }, status=status.HTTP_401_UNAUTHORIZED)

    def get_redirect_url(self, role):

        redirect_urls = {
            User.Role.ADMIN: '/admin/dashboard/',
            User.Role.RECEPTION: '/reception/dashboard/',
            User.Role.DOCTOR: '/doctor/dashboard/',
            User.Role.MANAGER: '/manager/dashboard/',
        }

        return redirect_urls.get(role, '/')

    def get_dashboard_type(self, role):

        dashboard_types = {
            User.Role.ADMIN: 'admin',
            User.Role.RECEPTION: 'reception',
            User.Role.DOCTOR: 'doctor',
            User.Role.MANAGER: 'manager',
        }

        return dashboard_types.get(role, 'unknown')


class CheckAuthView(APIView):
    """
    بررسی وضعیت احراز هویت کاربر
    """

    def get(self, request):

        if request.user.is_authenticated:

            return Response({
                'is_authenticated': True,
                'role': request.user.role,
                'username': request.user.username,
                'dashboard_type': self.get_dashboard_type(
                    request.user.role
                ),
                'redirect_url': self.get_redirect_url(
                    request.user.role
                )
            }, status=status.HTTP_200_OK)

        return Response({
            'is_authenticated': False
        }, status=status.HTTP_200_OK)

    def get_redirect_url(self, role):

        redirect_urls = {
            User.Role.ADMIN: '/admin/dashboard/',
            User.Role.RECEPTION: '/reception/dashboard/',
            User.Role.DOCTOR: '/doctor/dashboard/',
            User.Role.MANAGER: '/manager/dashboard/',
        }

        return redirect_urls.get(role, '/')

    def get_dashboard_type(self, role):

        dashboard_types = {
            User.Role.ADMIN: 'admin',
            User.Role.RECEPTION: 'reception',
            User.Role.DOCTOR: 'doctor',
            User.Role.MANAGER: 'manager',
        }

        return dashboard_types.get(role, 'unknown')