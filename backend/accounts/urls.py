from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    CurrentUserView,
    CheckAuthView,
    AdminUserListCreateView,
    AdminUserDetailView,
    AdminUserToggleActiveView,
    AdminDoctorListCreateView,
    AdminDoctorDetailView,
    AdminReceptionistListCreateView,
    AdminReceptionistDetailView,
)


app_name = 'accounts'


urlpatterns = [

    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/user/', CurrentUserView.as_view(), name='current-user'),
    path('api/check-auth/', CheckAuthView.as_view(), name='check-auth'),

    path('api/admin/users/', AdminUserListCreateView.as_view(), name='admin-user-list'),
    path('api/admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('api/admin/users/<int:pk>/toggle-active/', AdminUserToggleActiveView.as_view(), name='admin-user-toggle-active'),

    path('api/admin/doctors/', AdminDoctorListCreateView.as_view(), name='admin-doctor-list'),
    path('api/admin/doctors/<int:pk>/', AdminDoctorDetailView.as_view(), name='admin-doctor-detail'),

    path('api/admin/receptionists/', AdminReceptionistListCreateView.as_view(), name='admin-receptionist-list'),
    path('api/admin/receptionists/<int:pk>/', AdminReceptionistDetailView.as_view(), name='admin-receptionist-detail'),

]