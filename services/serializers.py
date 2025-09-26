# services/serializers.py
app_name = "services"

from rest_framework import serializers

from .models import Notice, Event, Ad, FAQ, PrivacyPolicy, Term

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            'id', 'service', 'title', 'subtitle', 'mobile_img', 'desktop_img', 
            'detail_img', 'description', 'link', 'start_date', 'end_date', 
            'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'service', 'title', 'subtitle', 'mobile_img', 'desktop_img', 
            'detail_img', 'description', 'link', 'start_date', 'end_date', 
            'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = [
            'id', 'service', 'title', 'subtitle', 'mobile_img', 'desktop_img', 
            'detail_img', 'background_img', 'description', 'link', 'start_date', 'end_date', 
            'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            'id', 'service', 'order', 'question', 'answer', 
            'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = [
            'id', 'service', 'order', 'subject', 'detail', 
            'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = [
            'id', 'service', 'order', 'subject', 'detail', 
            'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']