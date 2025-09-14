# users/views.py
app_name = 'users'

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from server.utils import ErrorResponseBuilder, SuccessResponseBuilder
from accounts.models import User

from .rules import RefferalRule
from .models import Referral, PointCoupon, PointTransaction
from .permissions import IsAuthenticated
from .serializers import ReferralSerializer, PointTransactionSerializer
from .schemas import UserSchema

class ReferralAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(**UserSchema.get_referrals())
    def get(self, request):
        referrals_given = Referral.objects.filter(referrer=request.user)
        referrals_received = Referral.objects.filter(referree=request.user)
        
        data = {
            'referrals_given': ReferralSerializer(referrals_given, many=True).data,
            'referrals_received': ReferralSerializer(referrals_received, many=True).data,
        }
        
        response = SuccessResponseBuilder().with_message("추천인 조회 성공").with_data({"referral": data}).build()
        return Response(response, status=status.HTTP_200_OK)


class ReferralDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**UserSchema.create_referral())
    def post(self, request, referral_code):
        user = request.user
        if user.referral_code == referral_code:
            response = ErrorResponseBuilder().with_message("자기 자신을 추천할 수 없습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if Referral.objects.filter(referrer=user).exists():
            response = ErrorResponseBuilder().with_message("한 명만 추천할 수 있습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        referree = get_object_or_404(User, referral_code=referral_code)
        referral_rule = RefferalRule(user, referree)
        referral = referral_rule.create()
        
        response = SuccessResponseBuilder().with_message("추천인 등록 성공").with_data({"referral": ReferralSerializer(referral).data}).build()
        return Response(response, status=status.HTTP_201_CREATED)


class PointCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**UserSchema.use_coupon())
    def post(self, request, coupon_code):
        coupon = get_object_or_404(PointCoupon, code=coupon_code, is_active=True)

        used_count = PointTransaction.objects.filter(transaction_id=coupon.id, transaction_type='COUPON').count()
        if used_count >= coupon.usage_limit:
            response = ErrorResponseBuilder().with_message("쿠폰을 사용할 수 없습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        user_used_count = PointTransaction.objects.filter(user=request.user, transaction_id=coupon.id, transaction_type='COUPON').count()
        if user_used_count >= coupon.usage_limit_per_user:
            response = ErrorResponseBuilder().with_message("쿠폰 사용 한도를 초과했습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not coupon.is_valid_now:
            response = ErrorResponseBuilder().with_message("유효하지 않은 쿠폰입니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        PointTransaction.objects.create(user=request.user, transaction_id=coupon.id, amount=coupon.amount, transaction_type='COUPON')
        response = SuccessResponseBuilder().with_message("쿠폰 사용 성공").build()
        return Response(response, status=status.HTTP_200_OK)


class PointTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**UserSchema.get_point_transactions())
    def get(self, request):
        transactions = PointTransaction.objects.filter(user=request.user)
        response = SuccessResponseBuilder().with_message("포인트 내역 조회 성공").with_data({"point_transaction": PointTransactionSerializer(transactions, many=True).data}).build()
        return Response(response, status=status.HTTP_200_OK)