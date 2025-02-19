# accounts/permissions.py
app_name = 'accounts'

from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verify if request is POST or PUT or DELETE.
        if request.method in ['POST', 'PUT', 'DELETE']:
            return request.user.is_authenticated and request.user.is_staff
        
        return request.user.is_authenticated  # GET request is allowed to all users.
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_staff