from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminPatientViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r'admin/patients', AdminPatientViewSet, basename='admin-patients')

urlpatterns = [
    path('api/', include(router.urls)),
]