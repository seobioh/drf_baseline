# server/schemas.py
app_name = "server"

import re

from rest_framework import status, serializers

# Success Response Serializer
class SuccessResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=0, help_text="Success code")
    message = serializers.CharField(help_text="Success message")
    data = serializers.DictField(required=False, allow_null=True, help_text="Response data")
    
    class Meta:
        ref_name = "SuccessResponse"
    
    def __init__(self, *args, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            if 'code' not in kwargs['data']:
                kwargs['data']['code'] = 0
        super().__init__(*args, **kwargs)


# Error Response Serializer
class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=1, help_text="Error code")
    message = serializers.CharField(help_text="Error message")
    errors = serializers.DictField(required=False, allow_null=True, help_text="Detailed error information")
    
    class Meta:
        ref_name = "ErrorResponse"
    
    def __init__(self, *args, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            if 'code' not in kwargs['data']:
                kwargs['data']['code'] = 1
        super().__init__(*args, **kwargs)