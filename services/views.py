# services/views.py
app_name = "services"

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Notice, Event, Ad, FAQ, PrivacyPolicy, Term
from .serializers import NoticeSerializer, EventSerializer, AdSerializer
from .serializers import FAQSerializer, PrivacyPolicySerializer, TermSerializer

class NoticeAPIView(APIView):
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            notices = Notice.objects.filter(is_active=True, service=service).order_by('-created_at')
        else:
            notices = Notice.objects.filter(is_active=True).order_by('-created_at')
        
        serializer = NoticeSerializer(notices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NoticeDetailAPIView(APIView):
    def get(self, request, notice_id):
        notice = get_object_or_404(Notice, id=notice_id, is_active=True)
        serializer = NoticeSerializer(notice)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventAPIView(APIView):
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            events = Event.objects.filter(is_active=True, service=service).order_by('-created_at')
        else:
            events = Event.objects.filter(is_active=True).order_by('-created_at')
        
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventDetailAPIView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id, is_active=True)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdAPIView(APIView):
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            ads = Ad.objects.filter(is_active=True, service=service).order_by('-created_at')
        else:
            ads = Ad.objects.filter(is_active=True).order_by('-created_at')
        
        serializer = AdSerializer(ads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdDetailAPIView(APIView):
    def get(self, request, ad_id):
        ad = get_object_or_404(Ad, id=ad_id, is_active=True)
        serializer = AdSerializer(ad)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FAQAPIView(APIView):
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            faqs = FAQ.objects.filter(is_active=True, service=service).order_by('service', 'order')
        else:
            faqs = FAQ.objects.filter(is_active=True).order_by('service', 'order')
        
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FAQDetailAPIView(APIView):
    def get(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id, is_active=True)
        serializer = FAQSerializer(faq)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivacyPolicyAPIView(APIView):
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            privacys = PrivacyPolicy.objects.filter(is_active=True, service=service).order_by('service', 'order')
        else:
            privacys = PrivacyPolicy.objects.filter(is_active=True).order_by('service', 'order')
        
        serializer = PrivacyPolicySerializer(privacys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivacyPolicyDetailAPIView(APIView):
    def get(self, request, privacy_policy_id):
        privacy = get_object_or_404(PrivacyPolicy, id=privacy_policy_id, is_active=True)
        serializer = PrivacyPolicySerializer(privacy)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TermAPIView(APIView):
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            terms = Term.objects.filter(is_active=True, service=service).order_by('service', 'order')
        else:
            terms = Term.objects.filter(is_active=True).order_by('service', 'order')
        
        serializer = TermSerializer(terms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TermDetailAPIView(APIView):
    def get(self, request, term_id):
        term = get_object_or_404(Term, id=term_id, is_active=True)
        serializer = TermSerializer(term)
        return Response(serializer.data, status=status.HTTP_200_OK)