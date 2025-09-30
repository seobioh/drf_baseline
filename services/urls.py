# services/urls.py
app_name = 'services'

from django.urls import path

from .views import NoticeAPIView, NoticeDetailAPIView
from .views import EventAPIView, EventDetailAPIView
from .views import AdAPIView, AdDetailAPIView
from .views import FAQAPIView, FAQDetailAPIView
from .views import PrivacyPolicyAPIView, PrivacyPolicyDetailAPIView
from .views import TermAPIView, TermDetailAPIView
from .views import GPTAPIView

urlpatterns = [
    path('/notices', NoticeAPIView.as_view(), name='notice'),
    path('/notices/<int:notice_id>', NoticeDetailAPIView.as_view(), name='notice-detail'),
    
    path('/events', EventAPIView.as_view(), name='event'),
    path('/events/<int:event_id>', EventDetailAPIView.as_view(), name='event-detail'),
    
    path('/ads', AdAPIView.as_view(), name='ad'),
    path('/ads/<int:ad_id>', AdDetailAPIView.as_view(), name='ad-detail'),
    
    path('/faqs', FAQAPIView.as_view(), name='faq'),
    path('/faqs/<int:faq_id>', FAQDetailAPIView.as_view(), name='faq-detail'),
    
    path('/privacy-policies', PrivacyPolicyAPIView.as_view(), name='privacy-policy'),
    path('/privacy-policies/<int:privacy_policy_id>', PrivacyPolicyDetailAPIView.as_view(), name='privacy-policy-detail'),
    
    path('/terms', TermAPIView.as_view(), name='term'),
    path('/terms/<int:term_id>', TermDetailAPIView.as_view(), name='term-detail'),

    path('/gpt/<int:gpt_prompt_id>', GPTAPIView.as_view(), name='gpt'),
]