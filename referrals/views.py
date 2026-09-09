from core.models import Patient, Doctor, Department
from referrals.models import Referral
from .serializers import PatientReferralSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

class DoctorPatientsSerializer(serializers.ModelSerializer):
    referral_count = serializers.IntegerField()
    last_referral_date = serializers.DateTimeField()
    
    class Meta:
        model = Patient
        fields = ['id', 'national_id', 'full_name', 'phone', 'gender', 
                 'birth_date', 'referral_count', 'last_referral_date']

class DoctorPatientsListView(ListAPIView):
    """
    دریافت لیست بیماران یک دکتر با تعداد ارجاع‌ها
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorPatientsSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # بررسی اینکه کاربر نقش پزشک دارد
        if user.role != user.Role.DOCTOR:
            # اگر کاربر پذیرش یا ادمین است، می‌تواند بیماران همه دکترها را ببیند
            # یا می‌توانید اجازه دهید فقط پزشک خودش را ببیند
            pass
        
        try:
            doctor = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            return Patient.objects.none()
        
        # دریافت بیمارانی که به این دکتر ارجاع داده شده‌اند
        # با شمارش تعداد ارجاع‌ها و آخرین تاریخ ارجاع
        from django.db.models import Count, Max
        
        patients = Patient.objects.filter(
            referrals__doctor=doctor
        ).annotate(
            referral_count=Count('referrals'),
            last_referral_date=Max('referrals__referral_date')
        ).order_by('-last_referral_date')
        
        return patients
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'patients': serializer.data
        })





class PatientReferralCreateView(APIView):
    """
    ثبت بیمار و ارجاع همزمان
    اگر بیمار با کد ملی وجود داشت → فقط ارجاع ثبت می‌شود
    اگر بیمار وجود نداشت → هم بیمار و هم ارجاع ثبت می‌شوند
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        # 1. اعتبارسنجی داده‌های ورودی
        serializer = PatientReferralSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # 2. بررسی وجود بیمار با کد ملی
        try:
            patient = Patient.objects.get(national_id=data['national_id'])
            is_new_patient = False
        except Patient.DoesNotExist:
            patient = None
            is_new_patient = True
        
        # 3. ثبت بیمار اگر وجود نداشت
        if is_new_patient:
            patient = Patient.objects.create(
                national_id=data['national_id'],
                full_name=data['full_name'],
                phone=data.get('phone', ''),
                gender=data['gender'],
                birth_date=data.get('birth_date')
            )
        
        # 4. دریافت دکتر و بخش
        doctor = Doctor.objects.get(id=data['doctor_id'])
        department = Department.objects.get(code=data['department_code'])
        
        # 5. ثبت ارجاع جدید
        referral = Referral.objects.create(
            patient=patient,
            doctor=doctor,
            department=department,
            referral_date=data['referral_date'],
            expiry_date=data['expiry_date'],
            description=data.get('description', ''),
            status=Referral.Status.REGISTERED,
            reception_user=request.user
        )
        
        # 6. پاسخ موفق
        return Response({
            'status': 'success',
            'message': 'ارجاع با موفقیت ثبت شد',
            'data': {
                'patient': {
                    'id': patient.id,
                    'national_id': patient.national_id,
                    'full_name': patient.full_name,
                    'is_new': is_new_patient
                },
                'referral': {
                    'id': referral.id,
                    'referral_date': referral.referral_date,
                    'expiry_date': referral.expiry_date,
                    'status': referral.status,
                    'doctor': {
                        'id': doctor.id,
                        'name': f"{doctor.user.first_name} {doctor.user.last_name}",
                        'medical_code': doctor.medical_code
                    },
                    'department': {
                        'id': department.id,
                        'name': department.name,
                        'code': department.code
                    }
                }
            }
        }, status=status.HTTP_201_CREATED)