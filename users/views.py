# users/views.py
app_name = 'users'

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from accounts.models import User

from .models import Referral
from .permissions import IsAuthenticated
from .serializers import ReferralSerializer

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
            return Response({'error': 'Cannot refer yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Referral.objects.filter(referrer=user).exists():
            return Response({'error': 'You can only refer one person'}, status=status.HTTP_400_BAD_REQUEST)

        referree = get_object_or_404(User, referral_code=referral_code)
        referral = Referral.objects.create(referrer=user, referree=referree)
        
        return Response(ReferralSerializer(referral).data,  status=status.HTTP_201_CREATED)