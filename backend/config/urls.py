from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.middleware.csrf import get_token
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def csrf_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


def admin_logout_redirect(request):
    """logout ادمین → برگرد به لاگین React"""
    logout(request)
    return redirect('http://localhost:5173/')


urlpatterns = [
    path('admin/logout/', admin_logout_redirect, name='admin-logout'),

    path('admin/', admin.site.urls),
    path('api/csrf/', csrf_view, name='csrf'),
    path('', include('accounts.urls')),
    path('', include('core.urls')),
    path('', include('referrals.urls')),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
]