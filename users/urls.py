# users/urls.py
app_name = 'users'

from django.urls import path

from .views import ReferralAPIView, ReferralDetailAPIView
from .views import PointCouponAPIView, PointTransactionAPIView

urlpatterns = [
    path('/referrals', ReferralAPIView.as_view(), name='referral'),
    path('/referrals/<str:referral_code>', ReferralDetailAPIView.as_view(), name='referral-detail'),

    path('/point-coupons/<str:coupon_code>', PointCouponAPIView.as_view(), name='point-coupon'),
    path('/point-transactions', PointTransactionAPIView.as_view(), name='point-transaction'),
]
