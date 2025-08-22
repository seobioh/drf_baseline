# users/serializers.py
app_name = 'users'

from rest_framework import serializers

from .models import Referral

class ReferralSerializer(serializers.ModelSerializer):
    referrer_username = serializers.SerializerMethodField()
    referree_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Referral
        fields = ['referrer', 'referrer_username', 'referree', 'referree_username', 'created_at', 'modified_at']
        read_only_fields = ['referrer', 'referrer_username', 'referree', 'referree_username', 'created_at', 'modified_at']
    
    def get_referrer_username(self, obj):
        return obj.referrer.username if obj.referrer else None
    
    def get_referree_username(self, obj):
        return obj.referree.username if obj.referree else None