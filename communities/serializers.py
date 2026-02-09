# communities/serializers.py
app_name = "communities"

import uuid
from rest_framework import serializers

from .models import Community, Member, FollowStatus, Follow
from .models import PostCategory, Post, PostLike, PostScrap, PostComment, PostCommentLike, PostReply, PostReplyLike

# Community
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'


class CommunitySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['id', 'name', 'image', 'description', 'member_count', 'favorite_count', 'post_count', 'score']


class MemberSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['user', 'community', 'created_at', 'modified_at', 'is_active', 'is_staff', 'is_admin']

    def create(self, validated_data):
        if not validated_data.get("nickname"):
            community = validated_data.get("community")
            if community:
                base = community.name.replace(" ", "")[:10]  # 공백 제거 + 최대 10자
            else:
                base = "멤버"
            validated_data["nickname"] = self.generate_unique_nickname(base)
        return super().create(validated_data)

    def generate_unique_nickname(self, base):
        while True:
            nickname = f"{base}{uuid.uuid4().hex[:6]}"
            if not Member.objects.filter(nickname=nickname).exists():
                return nickname


class MemberListSerializer(MemberSerializer):
    community = CommunitySimpleSerializer(read_only=True)

    class Meta(MemberSerializer.Meta):
        fields = MemberSerializer.Meta.fields
        read_only_fields = MemberSerializer.Meta.read_only_fields


class MemberSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'nickname', 'profile_image']
        read_only_fields = ['id', 'nickname', 'profile_image']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'status', 'created_at', 'modified_at']
        read_only_fields = ['id', 'status', 'created_at', 'modified_at']


# Post
# <-------------------------------------------------------------------------------------------------------------------------------->
class PostCategorySimpleSerializer(serializers.ModelSerializer):
     class Meta:
        model = PostCategory
        fields = ['id', 'name', 'image', 'description', 'favorite_count', 'post_count', 'score']
        read_only_fields = ['id', 'name', 'image', 'description', 'favorite_count', 'post_count', 'score']


class PostCategorySerializer(serializers.ModelSerializer):
    parent = PostCategorySimpleSerializer(read_only=True)

    class Meta:
        model = PostCategory
        fields = ['id', 'parent', 'name', 'description', 'image', 'favorite_count', 'post_count', 'score', 'created_at', 'modified_at']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'category', 'author', 'title', 'content', 'images', 'is_anonymous']
        read_only_fields = ['id', 'category', 'author', 'created_at', 'modified_at']


class PostListSerializer(serializers.ModelSerializer):
    author = MemberSimpleSerializer(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    is_scraped = serializers.BooleanField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'like_count', 'comment_count', 'scrap_count', 'score', 'is_liked', 'is_scraped', 'is_following', 'created_at', 'modified_at']


class PostDetailSerializer(serializers.ModelSerializer):
    author = MemberSimpleSerializer(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    is_scraped = serializers.BooleanField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'category', 'title', 'content', 'images', 'author', 'like_count', 'comment_count', 'reply_count', 'scrap_count', 'score', 'is_liked', 'is_scraped', 'is_following', 'created_at', 'modified_at']

    

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['id', 'post', 'member', 'created_at']
        read_only_fields = ['id', 'post', 'created_at', 'member']


class PostScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostScrap
        fields = ['id', 'post', 'member', 'created_at']
        read_only_fields = ['id', 'post', 'created_at', 'member']


class PostCommentSerializer(serializers.ModelSerializer):
    author = MemberSimpleSerializer(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'post', 'content', 'image', 'author', 'like_count', 'reply_count', 'score', 'is_liked', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'post', 'author', 'created_at', 'modified_at', 'is_active']


class PostReplySerializer(serializers.ModelSerializer):
    author = MemberSimpleSerializer(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = PostReply
        fields = ['id', 'comment', 'content', 'image', 'author', 'like_count', 'score', 'is_liked', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'comment', 'author', 'created_at', 'modified_at', 'is_active']