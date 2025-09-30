# services/views.py
app_name = "services"

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from server.utils import SuccessResponseBuilder

from .utils import GPTService
from .models import Notice, Event, Ad, FAQ, PrivacyPolicy, Term, GPTPrompt
from .serializers import NoticeSerializer, EventSerializer, AdSerializer
from .serializers import FAQSerializer, PrivacyPolicySerializer, TermSerializer
from .schemas import ServicesSchema

class NoticeAPIView(APIView):
    @extend_schema(**ServicesSchema.get_notices())
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            notices = Notice.objects.filter(is_active=True, service=service).order_by('-created_at')
        else:
            notices = Notice.objects.filter(is_active=True).order_by('-created_at')
        
        serializer = NoticeSerializer(notices, many=True)
        response = SuccessResponseBuilder().with_message("공지사항 조회 성공").with_data({"notices": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class NoticeDetailAPIView(APIView):
    @extend_schema(**ServicesSchema.get_notice_detail())
    def get(self, request, notice_id):
        notice = get_object_or_404(Notice, id=notice_id, is_active=True)
        serializer = NoticeSerializer(notice)
        response = SuccessResponseBuilder().with_message("공지사항 조회 성공").with_data({"notice": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class EventAPIView(APIView):
    @extend_schema(**ServicesSchema.get_events())
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            events = Event.objects.filter(is_active=True, service=service).order_by('-created_at')
        else:
            events = Event.objects.filter(is_active=True).order_by('-created_at')
        
        serializer = EventSerializer(events, many=True)
        response = SuccessResponseBuilder().with_message("이벤트 조회 성공").with_data({"events": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class EventDetailAPIView(APIView):
    @extend_schema(**ServicesSchema.get_event_detail())
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id, is_active=True)
        serializer = EventSerializer(event)
        response = SuccessResponseBuilder().with_message("이벤트 조회 성공").with_data({"event": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class AdAPIView(APIView):
    @extend_schema(**ServicesSchema.get_ads())
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            ads = Ad.objects.filter(is_active=True, service=service).order_by('-created_at')
        else:
            ads = Ad.objects.filter(is_active=True).order_by('-created_at')
        
        serializer = AdSerializer(ads, many=True)
        response = SuccessResponseBuilder().with_message("광고 조회 성공").with_data({"ads": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class AdDetailAPIView(APIView):
    @extend_schema(**ServicesSchema.get_ad_detail())
    def get(self, request, ad_id):
        ad = get_object_or_404(Ad, id=ad_id, is_active=True)
        serializer = AdSerializer(ad)
        response = SuccessResponseBuilder().with_message("광고 조회 성공").with_data({"ad": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class FAQAPIView(APIView):
    @extend_schema(**ServicesSchema.get_faqs())
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            faqs = FAQ.objects.filter(is_active=True, service=service).order_by('service', 'order')
        else:
            faqs = FAQ.objects.filter(is_active=True).order_by('service', 'order')
        
        serializer = FAQSerializer(faqs, many=True)
        response = SuccessResponseBuilder().with_message("FAQ 조회 성공").with_data({"faqs": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class FAQDetailAPIView(APIView):
    @extend_schema(**ServicesSchema.get_faq_detail())
    def get(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id, is_active=True)
        serializer = FAQSerializer(faq)
        response = SuccessResponseBuilder().with_message("FAQ 조회 성공").with_data({"faq": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class PrivacyPolicyAPIView(APIView):
    @extend_schema(**ServicesSchema.get_privacy_policies())
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            privacys = PrivacyPolicy.objects.filter(is_active=True, service=service).order_by('service', 'order')
        else:
            privacys = PrivacyPolicy.objects.filter(is_active=True).order_by('service', 'order')
        
        serializer = PrivacyPolicySerializer(privacys, many=True)
        response = SuccessResponseBuilder().with_message("개인정보처리방침 조회 성공").with_data({"privacy_policies": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class PrivacyPolicyDetailAPIView(APIView):
    @extend_schema(**ServicesSchema.get_privacy_policy_detail())
    def get(self, request, privacy_policy_id):
        privacy = get_object_or_404(PrivacyPolicy, id=privacy_policy_id, is_active=True)
        serializer = PrivacyPolicySerializer(privacy)
        response = SuccessResponseBuilder().with_message("개인정보처리방침 조회 성공").with_data({"privacy_policy": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class TermAPIView(APIView):
    @extend_schema(**ServicesSchema.get_terms())
    def get(self, request):
        service = request.query_params.get('service')
        if service:
            terms = Term.objects.filter(is_active=True, service=service).order_by('service', 'order')
        else:
            terms = Term.objects.filter(is_active=True).order_by('service', 'order')
        
        serializer = TermSerializer(terms, many=True)
        response = SuccessResponseBuilder().with_message("이용약관 조회 성공").with_data({"terms": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class TermDetailAPIView(APIView):
    @extend_schema(**ServicesSchema.get_term_detail())
    def get(self, request, term_id):
        term = get_object_or_404(Term, id=term_id, is_active=True)
        serializer = TermSerializer(term)
        response = SuccessResponseBuilder().with_message("이용약관 조회 성공").with_data({"term": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)


class GPTAPIView(APIView):
    @extend_schema(**ServicesSchema.get_gpt_prompts())
    def post(self, request, gpt_prompt_id):
        gpt_prompt = get_object_or_404(GPTPrompt, id=gpt_prompt_id, is_active=True)
        gpt_service = GPTService()
        generator = gpt_service.generate_stream_response(gpt_prompt.prompt, request.data.get('message'))
        
        from django.http import StreamingHttpResponse
        response = StreamingHttpResponse(generator, content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response