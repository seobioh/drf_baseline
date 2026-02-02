# communities/permissions.py
app_name = 'communities'

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission

from .models import Member, Follow, FollowStatus

class IsSelf(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
 

class IsProfileReadable(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        current_member = get_object_or_404(Member, user=request.user, community=obj.community)

        # 1. 본인
        if obj == current_member:
            return True

        # 2. 상대가 나를 차단
        if Follow.objects.filter(follower=obj, following=current_member, status=FollowStatus.BLOCKED).exists():
            return False

        # 3. 공개 계정
        if not obj.is_private:
            return True

        # 4. 비공개 계정 → 팔로워만
        return Follow.objects.filter(follower=current_member, following=obj, status=FollowStatus.ACCEPTED).exists()