from django.urls import path
from .views import PatientReferralCreateView, DoctorPatientsListView, DoctorReferralsListView

app_name = 'referrals'

urlpatterns = [
    path(
        'api/referral/create/',
        PatientReferralCreateView.as_view(),
        name='referral-create'
    ),
    path(
        'api/doctor/patients/',
        DoctorPatientsListView.as_view(),
        name='doctor-patients'
    ),
    path('api/doctor/referrals/', DoctorReferralsListView.as_view(), name='doctor-referrals'),
]