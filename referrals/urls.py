from django.urls import path
from .views import PatientReferralCreateView

app_name = 'referrals'

urlpatterns = [
    path('api/referral/create/', PatientReferralCreateView.as_view(), name='referral-create'),
]