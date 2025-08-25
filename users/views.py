# users/views.py
app_name = 'users'

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from server.utils import ErrorResponseBuilder
from accounts.models import User

from .rules import RefferalRule
from .models import Referral, PointCoupon, PointTransaction
from .permissions import IsAuthenticated
from .serializers import ReferralSerializer, PointTransactionSerializer

class ReferralAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        referrals_given = Referral.objects.filter(referrer=request.user)
        referrals_received = Referral.objects.filter(referree=request.user)
        
        data = {
            'referrals_given': ReferralSerializer(referrals_given, many=True).data,
            'referrals_received': ReferralSerializer(referrals_received, many=True).data,
        }
        
        return Response(data, status=status.HTTP_200_OK)


class ReferralDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, referral_code):
        user = request.user
        if user.referral_code == referral_code:
            response = ErrorResponseBuilder().with_message("Cannot refer yourself").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if Referral.objects.filter(referrer=user).exists():
            response = ErrorResponseBuilder().with_message("You can only refer one person").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        referree = get_object_or_404(User, referral_code=referral_code)
        referral_rule = RefferalRule(user, referree)
        referral = referral_rule.create()
        
        return Response(ReferralSerializer(referral).data,  status=status.HTTP_201_CREATED)


class PointCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, coupon_code):
        coupon = get_object_or_404(PointCoupon, code=coupon_code, is_active=True)

        used_count = PointTransaction.objects.filter(transaction_id=coupon.id, transaction_type='COUPON').count()
        if used_count >= coupon.usage_limit:
            response = ErrorResponseBuilder().with_message("Coupon is not available").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        user_used_count = PointTransaction.objects.filter(user=request.user, transaction_id=coupon.id, transaction_type='COUPON').count()
        if user_used_count >= coupon.usage_limit_per_user:
            response = ErrorResponseBuilder().with_message("You have reached the usage limit for this coupon").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not coupon.is_valid_now:
            response = ErrorResponseBuilder().with_message("Coupon is not valid").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        PointTransaction.objects.create(user=request.user, transaction_id=coupon.id, amount=coupon.amount, transaction_type='COUPON')
        return Response({'message': 'Coupon used successfully'}, status=status.HTTP_200_OK)


class PointTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = PointTransaction.objects.filter(user=request.user)
        return Response(PointTransactionSerializer(transactions, many=True).data, status=status.HTTP_200_OK)