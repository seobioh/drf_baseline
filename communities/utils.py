# communities/utils.py
app_name = 'communities'

from django.db.models import Q, F
from django.shortcuts import get_object_or_404

from .models import Community, CommunityFavorite, Member, Follow, FollowStatus
from .models import PostCategory, PostCategoryFavorite, Post, PostLike, PostScrap, PostComment, PostReply, PostCommentLike, PostReplyLike

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
def get_object_with_permission(view, model, pk_value, request, pk_field='id', queryset=None):
    qs = queryset if queryset is not None else model.objects
    obj = get_object_or_404(qs, **{pk_field: pk_value})
    community = get_community_from_obj(obj)
    member = get_object_or_404(Member, user=request.user, community=community)
    obj._member = member
    view.check_object_permissions(request, obj)
    return obj


def get_member_from_obj(obj):
    return getattr(obj, '_member', None)


def get_blocked_member_ids(members):
    if not hasattr(members, '__iter__'):
        members = [members]

    member_ids = [m.id for m in members]

    return set(
        i for pair in
        Follow.objects.filter(
            Q(follower_id__in=member_ids, status=FollowStatus.BLOCKED) |
            Q(following_id__in=member_ids, status=FollowStatus.BLOCKED)
        ).values_list('follower_id', 'following_id')
        for i in pair if i not in member_ids
    )


# Helper function to increase count
def increase_count(obj):
    update_counts(obj, +1)


# Helper function to decrease count
def decrease_count(obj):
    update_counts(obj, -1)


# Helper function to update counts
def update_counts(obj, delta: int):
    if isinstance(obj, Member):
        Community.objects.filter(id=obj.community_id).update(member_count=F('member_count') + delta)

    elif isinstance(obj, CommunityFavorite):
        Community.objects.filter(id=obj.community_id).update(favorite_count=F('favorite_count') + delta)

    elif isinstance(obj, PostCategoryFavorite):
        PostCategory.objects.filter(id=obj.category_id).update(favorite_count=F('favorite_count') + delta)

    elif isinstance(obj, Post):
        Member.objects.filter(id=obj.author_id).update(post_count=F('post_count') + delta)
        Community.objects.filter(id=obj.category.community_id).update(post_count=F('post_count') + delta)
        PostCategory.objects.filter(id=obj.category_id).update(post_count=F('post_count') + delta)

    elif isinstance(obj, PostLike):
        Post.objects.filter(id=obj.post_id).update(like_count=F('like_count') + delta)
        Member.objects.filter(id=obj.member_id).update(like_count=F('like_count') + delta)

    elif isinstance(obj, PostScrap):
        Post.objects.filter(id=obj.post_id).update(scrap_count=F('scrap_count') + delta)
        Member.objects.filter(id=obj.member_id).update(scrap_count=F('scrap_count') + delta)

    elif isinstance(obj, PostComment):
        Post.objects.filter(id=obj.post_id).update(comment_count=F('comment_count') + delta)
        Member.objects.filter(id=obj.author_id).update(comment_count=F('comment_count') + delta)

    elif isinstance(obj, PostCommentLike):
        PostComment.objects.filter(id=obj.comment_id).update(like_count=F('like_count') + delta)

    elif isinstance(obj, PostReply):
        Post.objects.filter(id=obj.comment.post_id).update(reply_count=F('reply_count') + delta)
        PostComment.objects.filter(id=obj.comment_id).update(reply_count=F('reply_count') + delta)
        Member.objects.filter(id=obj.author_id).update(reply_count=F('reply_count') + delta)

    elif isinstance(obj, PostReplyLike):
        PostReply.objects.filter(id=obj.reply_id).update(like_count=F('like_count') + delta)

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")
