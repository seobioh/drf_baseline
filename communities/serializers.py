# communities/serializers.py
app_name = "communities"

import uuid
from rest_framework import serializers

from .models import Community, Member, FollowStatus, Follow

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