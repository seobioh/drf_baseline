# users/urls.py
app_name = 'users'

from django.urls import path

from .views import ReferralAPIView, ReferralDetailAPIView

urlpatterns = [
    path('/referrals', ReferralAPIView.as_view(), name='referral'),
    path('/referrals/<str:referral_code>', ReferralDetailAPIView.as_view(), name='referral-detail'),
]
