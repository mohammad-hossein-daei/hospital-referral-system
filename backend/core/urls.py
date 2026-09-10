from django.urls import path, include

urlpatterns = [
    # ... سایر URL ها
    path('', include('referral.urls')),
]