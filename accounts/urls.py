from django.urls import path
from .views import (
    LoginView, 
    LogoutView, 
    CurrentUserView,
    CheckAuthView
)

app_name = 'accounts'

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user/', CurrentUserView.as_view(), name='current-user'),
    path('api/check-auth/', CheckAuthView.as_view(), name='check-auth'),
]