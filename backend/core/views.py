from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from accounts.permissions import IsReactAdmin

from .models import Patient
from .serializers import PatientSerializer


class AdminPatientPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminPatientViewSet(viewsets.ModelViewSet):
    """
    API مدیریت بیماران برای پنل React Admin.

    فقط React Admin اجازه دسترسی دارد.
    """

    serializer_class = PatientSerializer
    permission_classes = [IsReactAdmin]
    pagination_class = AdminPatientPagination

    def get_queryset(self):
        queryset = Patient.objects.all().order_by("-created_at")

        search = self.request.query_params.get("search")
        gender = self.request.query_params.get("gender")

        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(national_id__icontains=search)
                | Q(phone__icontains=search)
            )

        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset