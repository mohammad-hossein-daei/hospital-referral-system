from core.models import Patient, Doctor, Department
from referrals.models import Referral
from .serializers import PatientReferralSerializer, ReferralSerializer
from .models import Referral   # ← اگر نبود
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.db import transaction
from django.db.models import Count, Max
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Serializers
# ═══════════════════════════════════════════════════════════

class DoctorPatientsSerializer(serializers.ModelSerializer):
    referral_count = serializers.IntegerField()
    last_referral_date = serializers.DateTimeField()

    class Meta:
        model = Patient
        fields = [
            'id', 'national_id', 'full_name', 'phone',
            'gender', 'birth_date', 'referral_count', 'last_referral_date',
        ]


# ═══════════════════════════════════════════════════════════
# Views
# ═══════════════════════════════════════════════════════════

class DoctorPatientsListView(ListAPIView):
    """
    دریافت لیست بیماران یک دکتر با تعداد ارجاع‌ها

    - پزشک: فقط بیماران خودش را می‌بیند
    - ادمین / پذیرش / مدیر: می‌توانند پارامتر `doctor_id` بفرستند
      تا بیماران آن پزشک را ببینند؛ در غیر این صورت خطا برمی‌گردد.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorPatientsSerializer

    def get_doctor(self, user, request):
        """
        تعیین دکتر بر اساس نقش کاربر
        خروجی: (doctor, error_response)
        """
        role = user.role

        # پزشک → فقط خودش
        if role == user.Role.DOCTOR:
            try:
                return Doctor.objects.get(user=user), None
            except Doctor.DoesNotExist:
                return None, Response({
                    'status': 'error',
                    'message': 'پروفایل پزشک برای این کاربر یافت نشد',
                }, status=status.HTTP_404_NOT_FOUND)

        # ادمین / پذیرش / مدیر → باید doctor_id بفرستند
        if role in [user.Role.ADMIN, user.Role.RECEPTION, user.Role.MANAGER]:
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return None, Response({
                    'status': 'error',
                    'message': 'پارامتر doctor_id الزامی است',
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                return Doctor.objects.get(id=doctor_id), None
            except Doctor.DoesNotExist:
                return None, Response({
                    'status': 'error',
                    'message': 'پزشک یافت نشد',
                }, status=status.HTTP_404_NOT_FOUND)

        # نقش ناشناخته
        return None, Response({
            'status': 'error',
            'message': 'شما دسترسی به این بخش ندارید',
        }, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        doctor, error = self.get_doctor(self.request.user, self.request)
        if error:
            # با return Patient.objects.none() جلوی خطای بعدی را می‌گیریم
            # اما خطا را در list() برمی‌گردانیم
            self._error_response = error
            return Patient.objects.none()

        self._error_response = None
        return (
            Patient.objects
            .filter(referrals__doctor=doctor)
            .annotate(
                referral_count=Count('referrals'),
                last_referral_date=Max('referrals__referral_date'),
            )
            .order_by('-last_referral_date')
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # اگر خطا داشتیم، همان را برگردان
        error = getattr(self, '_error_response', None)
        if error is not None:
            return error

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'patients': serializer.data,
        })


class PatientReferralCreateView(APIView):
    """
    ثبت بیمار و ارجاع همزمان

    - اگر بیمار با کد ملی وجود داشت → فقط ارجاع ثبت می‌شود
    - اگر بیمار وجود نداشت → هم بیمار و هم ارجاع ثبت می‌شوند
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # 1. اعتبارسنجی داده‌های ورودی
        serializer = PatientReferralSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 2. دریافت دکتر و بخش (قبل از ساخت بیمار، تا اگر خطا داد rollback شود)
        try:
            doctor = Doctor.objects.get(id=data['doctor_id'])
        except Doctor.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'پزشک یافت نشد',
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            department = Department.objects.get(code=data['department_code'])
        except Department.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'بخش یافت نشد',
            }, status=status.HTTP_404_NOT_FOUND)

        # 3. بررسی وجود بیمار با کد ملی
        patient = Patient.objects.filter(national_id=data['national_id']).first()
        is_new_patient = patient is None

        # 4. ثبت بیمار اگر وجود نداشت
        if is_new_patient:
            try:
                patient = Patient.objects.create(
                    national_id=data['national_id'],
                    full_name=data['full_name'],
                    phone=data.get('phone', ''),
                    gender=data['gender'],
                    birth_date=data.get('birth_date'),
                )
            except ValidationError as exc:
                # خطای اعتبارسنجی مدل (مثلاً کد ملی تکراری در لحظه)
                return Response({
                    'status': 'error',
                    'message': 'خطا در ثبت بیمار',
                    'errors': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                }, status=status.HTTP_400_BAD_REQUEST)

        # 5. ثبت ارجاع جدید
        try:
            referral = Referral.objects.create(
                patient=patient,
                doctor=doctor,
                department=department,
                referral_date=data['referral_date'],
                expiry_date=data['expiry_date'],
                description=data.get('description', ''),
                status=Referral.Status.REGISTERED,
            )
        except ValidationError as exc:
            return Response({
                'status': 'error',
                'message': 'خطا در ثبت ارجاع',
                'errors': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
            }, status=status.HTTP_400_BAD_REQUEST)

        # 6. پاسخ موفق
        return Response({
            'status': 'success',
            'message': 'ارجاع با موفقیت ثبت شد',
            'data': {
                'patient': {
                    'id': patient.id,
                    'national_id': patient.national_id,
                    'full_name': patient.full_name,
                    'is_new': is_new_patient,
                },
                'referral': {
                    'id': referral.id,
                    'referral_date': referral.referral_date,
                    'expiry_date': referral.expiry_date,
                    'status': referral.status,
                    'doctor': {
                        'id': doctor.id,
                        'name': f"{doctor.user.first_name} {doctor.user.last_name}".strip(),
                        'medical_code': doctor.medical_code,
                    },
                    'department': {
                        'id': department.id,
                        'name': department.name,
                        'code': department.code,
                    },
                },
            },
        }, status=status.HTTP_201_CREATED)

class DoctorReferralsListView(ListAPIView):
    """
    لیست ارجاع‌های یک پزشک
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role != user.Role.DOCTOR:
            return Referral.objects.none()

        try:
            doctor = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            return Referral.objects.none()

        return Referral.objects.filter(doctor=doctor).order_by('-referral_date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'referrals': serializer.data,
        })