# communities/utils.py
app_name = 'communities'

from django.shortcuts import get_object_or_404
from .models import Community, Member
from .models import PostCategory, Post, PostComment, PostReply

# Helper function to get community
def get_community_from_obj(obj):
    if isinstance(obj, Community):
        return obj

    if isinstance(obj, PostCategory):
        return obj.community
    if isinstance(obj, Post):
        return obj.category.community
    if isinstance(obj, PostComment):
        return obj.post.category.community
    if isinstance(obj, PostReply):
        return obj.comment.post.category.community

    return None


# Helper function to get object with permission check
def get_object_with_permission(view, model, pk_value, request, pk_field='id'):
    obj = get_object_or_404(model, **{pk_field: pk_value})
    community = get_community_from_obj(obj)
    member = get_object_or_404(Member, user=request.user, community=community)
    obj._member = member
    view.check_object_permissions(request, obj)
    return obj