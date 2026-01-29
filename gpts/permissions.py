# gpts/permissions.py
app_name = 'gpts'

from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission

class IsGPTChatRoomOwner(BasePermission):
    def has_permission(self, request, view):   
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.user