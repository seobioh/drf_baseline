# communities/views.py
app_name = 'communities'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db import transaction
from django.db.models import Q, F, Exists, OuterRef
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from server.utils import SuccessResponseBuilder, ErrorResponseBuilder

from .utils import get_object_with_permission, get_member_from_obj, get_blocked_member_ids, increase_count, decrease_count
from .models import Community, CommunityFavorite, Member, Follow, FollowStatus
from .models import PostCategory, PostCategoryFavorite, Post, PostLike, PostScrap, PostComment, PostCommentLike, PostReply, PostReplyLike
from .paginations import FollowerCursorPagination, FollowingCursorPagination
from .paginations import PostPagination, PostCommentPagination, PostReplyPagination
from .schemas import CommunitySchema, MemberSchema, FollowerSchema, FollowingSchema, BlockSchema
from .schemas import PostCategorySchema, PostSchema, PostCommentSchema, PostReplySchema
from .serializers import CommunitySerializer, MemberSerializer, MemberListSerializer, MemberSimpleSerializer, FollowSerializer
from .serializers import PostCategorySerializer, PostSerializer, PostListSerializer, PostDetailSerializer, PostCommentSerializer, PostReplySerializer
from .permissions import AllowAny, IsAuthenticated, IsSelf, IsProfileReadable
from .permissions import IsMember, IsMemberAuthor

# Community APIView
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommunityAPIView(APIView):
    permission_classes = [AllowAny]
    
    # 커뮤니티 목록 조회: 누구나 가능
    @extend_schema(**CommunitySchema.get_communities())
    def get(self, request):
        communities = Community.objects.all()
        serializer = CommunitySerializer(communities, many=True)
        response = SuccessResponseBuilder().with_message("커뮤니티 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Community Detail APIView
class CommunityDetailAPIView(APIView):
    permission_classes = [AllowAny]

    # 커뮤니티 상세 조회: 누구나 가능
    @extend_schema(**CommunitySchema.get_community_detail())
    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        serializer = CommunitySerializer(community)
        response = SuccessResponseBuilder().with_message("커뮤니티 상세 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


#  Favorite Community APIView
class FavoriteCommunityAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    # Community 즐겨찾기 여부 조회: 멤버이면서 본인만 가능
    @extend_schema(**CommunitySchema.get_favorite_status())
    def get(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        member = get_member_from_obj(community)
        favored = CommunityFavorite.objects.filter(member=member).exists()
        response = SuccessResponseBuilder().with_message("커뮤니티 즐겨찾기 여부 조회 성공").with_data({"favored": favored}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Community 즐겨찾기: 멤버이면서 본인만 가능
    @extend_schema(**CommunitySchema.create_favorite())
    def post(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        community_favorite, created = CommunityFavorite.objects.get_or_create(member=get_member_from_obj(community), community=community)
        if created:
            increase_count(community_favorite)
        response = SuccessResponseBuilder().with_message("커뮤니티 즐겨찾기 성공").with_data({"favored": True}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Community 즐겨찾기 취소: 멤버이면서 본인만 가능
    @extend_schema(**CommunitySchema.delete_favorite())
    def delete(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        community_favorite = CommunityFavorite.objects.filter(member=get_member_from_obj(community), community=community).first()
        if community_favorite:
            decrease_count(community_favorite)
            community_favorite.delete()
        response = SuccessResponseBuilder().with_message("커뮤니티 즐겨찾기 취소 성공").with_data({"favored": False}).build()
        return Response(response, status=status.HTTP_200_OK)


# Favorite Community List API View
class FavoriteCommunityListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 즐겨찾기 한 커뮤니티 목록
    @extend_schema(**CommunitySchema.get_favorite_list())
    def get(self, request):
        members = Member.objects.filter(user=request.user)
        favorites = CommunityFavorite.objects.filter(member__in=members).distinct()
        communities = [favorite.community for favorite in favorites]
        serializer = CommunitySerializer(communities, many=True)
        response = SuccessResponseBuilder().with_message("즐겨찾기 한 커뮤니티 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Member APIView
# <-------------------------------------------------------------------------------------------------------------------------------->
class MemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 멤버 전체 목록 조회: 멤버만 가능
    @extend_schema(**MemberSchema.get_members())
    def get(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        member = get_member_from_obj(community)
        blocked_ids = Follow.objects.filter(Q(follower=member, status=FollowStatus.BLOCKED) | Q(following=member, status=FollowStatus.BLOCKED)).values_list('follower_id', 'following_id')
        blocked_member_ids = {i for pair in blocked_ids for i in pair if i != member.id}
        members = Member.objects.filter(community=community).exclude(id__in=blocked_member_ids)
        serializer = MemberSimpleSerializer(members, many=True)
        response = SuccessResponseBuilder().with_message("멤버 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # 멤버 등록: 본인만 가능
    @extend_schema(**MemberSchema.create_member())
    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        if Member.objects.filter(user=request.user, community=community).exists():
            response = ErrorResponseBuilder().with_message("이미 가입된 멤버입니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save(community=community, user=request.user, is_staff=request.user.is_staff, is_admin=request.user.is_admin)
            increase_count(member)
            response = SuccessResponseBuilder().with_message("멤버 등록 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_201_CREATED)

        response = ErrorResponseBuilder().with_message("멤버 등록 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Member List APIView
class MemberListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 내가 속한 멤버 목록 조회
    @extend_schema(**MemberSchema.get_member_list())
    def get(self, request):
        members = Member.objects.filter(user=request.user)
        serializer = MemberListSerializer(members, many=True)
        response = SuccessResponseBuilder().with_message("내가 속한 멤버 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Member Detail APIView
class MemberDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsProfileReadable()]
        return [IsSelf()]
    
    # 멤버 정보 조회: 비공개일 경우 본인 + 팔로워에게 공개, 공개일 경우 모두에게 공개
    @extend_schema(**MemberSchema.get_member_detail())
    def get(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        serializer = MemberSerializer(member)
        response = SuccessResponseBuilder().with_message("멤버 정보 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # 멤버 정보 수정: 본인만 가능
    @extend_schema(**MemberSchema.update_member())
    def put(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(is_active=member.is_active, is_staff=request.user.is_staff, is_admin=request.user.is_admin)
            response = SuccessResponseBuilder().with_message("멤버 정보 수정 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_200_OK)
        response = ErrorResponseBuilder().with_message("멤버 정보 수정 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # 멤버 탈퇴: 본인만 가능
    @extend_schema(**MemberSchema.delete_member())
    def delete(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        decrease_count(member)
        member.delete()
        response = SuccessResponseBuilder().with_message("멤버 탈퇴 성공").build()
        return Response(response, status=status.HTTP_200_OK)


# Follower APIView
class FollowerAPIView(APIView):
    permission_classes = [IsProfileReadable]
    pagination_class = FollowerCursorPagination

    # 팔로워 목록 조회
    @extend_schema(**FollowerSchema.get_followers())
    def get(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)

        # 1. 본인인 경우, 팔로워 목록과 팔로우 요청 목록 모두 조회
        if member.user == request.user:
            followers = member.followers.filter(status__in=[FollowStatus.ACCEPTED, FollowStatus.PENDING]).order_by('-id')

        # 2. 본인이 아닌 경우, 팔로워 목록만 조회
        else:
            followers = member.followers.filter(status=FollowStatus.ACCEPTED).order_by('-id')
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(followers, request, view=self)
        if page is not None:
            serializer = FollowSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("팔로워 목록 조회 성공").with_data(serializer.data).with_cursor_pagination(paginator).build()
            return Response(response, status=status.HTTP_200_OK)

        serializer = FollowSerializer(followers, many=True)
        response = SuccessResponseBuilder().with_message("팔로워 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Follower Detail APIView
class FollowerDetailAPIView(APIView):
    permission_classes = [IsSelf]

    # 팔로잉 요청 수락
    @extend_schema(**FollowerSchema.accept_follower())
    def put(self, request, member_id, follower_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        follower = get_object_or_404(Member, id=follower_id)

        try:
            follow = Follow.objects.get(follower=follower, following=member, status=FollowStatus.PENDING)
        except Follow.DoesNotExist:
            response = ErrorResponseBuilder().with_message("팔로우 요청이 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            follow.status = FollowStatus.ACCEPTED
            follow.save(update_fields=["status"])
            Member.objects.filter(id=member.id).update(follower_count=F('follower_count') + 1)
            Member.objects.filter(id=follower.id).update(following_count=F('following_count') + 1)

        response = SuccessResponseBuilder().with_message("팔로우 요청 수락 성공").with_data(FollowSerializer(follow).data).build()
        return Response(response, status=status.HTTP_200_OK)

    # 팔로워 삭제
    @extend_schema(**FollowerSchema.delete_follower())
    def delete(self, request, member_id, follower_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        follower = get_object_or_404(Member, id=follower_id)

        with transaction.atomic():
            deleted, _ = member.followers.filter(follower=follower).delete()
            if deleted:
                Member.objects.filter(id=member.id).update(follower_count=F('follower_count') - 1)
                Member.objects.filter(id=follower.id).update(following_count=F('following_count') - 1)

        response = SuccessResponseBuilder().with_message("팔로워 삭제 성공").build()
        return Response(response, status=status.HTTP_200_OK)


# Following APIView
class FollowingAPIView(APIView):
    permission_classes = [IsProfileReadable]
    pagination_class = FollowingCursorPagination

    # 팔로잉 목록 조회
    @extend_schema(**FollowingSchema.get_followings())
    def get(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)

        # 1. 본인인 경우, 팔로잉 목록과 팔로우 요청 모두 조회
        if member.user == request.user:
            followings = member.followings.filter(status__in=[FollowStatus.ACCEPTED, FollowStatus.PENDING]).order_by('-id')

        # 2. 본인이 아닌 경우, 팔로잉 목록만 조회
        else:
            followings = member.followings.filter(status=FollowStatus.ACCEPTED).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(followings, request, view=self)
        if page is not None:
            serializer = FollowSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("팔로잉 목록 조회 성공").with_data(serializer.data).with_cursor_pagination(paginator).build()
            return Response(response, status=status.HTTP_200_OK)

        serializer = FollowSerializer(followings, many=True)
        response = SuccessResponseBuilder().with_message("팔로잉 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Following Detail APIView
class FollowingDetailAPIView(APIView):
    permission_classes = [IsSelf]

    # 팔로우 요청
    @extend_schema(**FollowingSchema.create_following())
    def post(self, request, member_id, following_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        following = get_object_or_404(Member, id=following_id)

        # 1. 팔로우 하려는 대상이 자기 자신인 경우
        if member == following:
            response = ErrorResponseBuilder().with_message("자기 자신을 팔로우할 수 없습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # 2. 내가 팔로우 요청을 이미 보낸 경우
        if Follow.objects.filter(follower=member, following=following, status=FollowStatus.PENDING).exists():
            response = ErrorResponseBuilder().with_message("이미 팔로우 요청이 존재합니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # 3. 내가 팔로우 대상을 차단한 경우
        if Follow.objects.filter(follower=member, following=following, status=FollowStatus.BLOCKED).exists():
            response = ErrorResponseBuilder().with_message("내가 차단한 사용자입니다.").build()
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # 4. 팔로우 하려는 대상에게 차단된 경우
        if Follow.objects.filter(follower=following, following=member, status=FollowStatus.BLOCKED).exists():
            response = ErrorResponseBuilder().with_message("이 사용자에게 차단되었습니다.").build()
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # 팔로우 하려는 대상이 비공개 계정인 경우
        if following.is_private:
            serializer = FollowSerializer(data={'follower': member_id, 'following': following_id, 'status': FollowStatus.PENDING})
            serializer.is_valid(raise_exception=True)
            follow = serializer.save()
            response = SuccessResponseBuilder().with_message("팔로우 요청 성공").with_data(FollowSerializer(follow).data).build()
            return Response(response, status=status.HTTP_201_CREATED)

        # 팔로우 하려는 대상이 공개 계정인 경우
        serializer = FollowSerializer(data={'follower': member_id, 'following': following_id})
        serializer.is_valid(raise_exception=True)
        follow = serializer.save()
        Member.objects.filter(id=member.id).update(following_count=F('following_count') + 1)
        Member.objects.filter(id=following.id).update(follower_count=F('follower_count') + 1)
        response = SuccessResponseBuilder().with_message("팔로우 성공").build()
        return Response(response, status=status.HTTP_201_CREATED)
    
    # 팔로우 취소
    @extend_schema(**FollowingSchema.delete_following())
    def delete(self, request, member_id, following_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        following = get_object_or_404(Member, id=following_id)
        follow = member.followings.filter(following=following).first()

        # 팔로우되지 않은 경우
        if not follow:
            response = ErrorResponseBuilder().with_message("팔로우되지 않았습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        was_accepted = follow.status == FollowStatus.ACCEPTED
        follow.delete()

        # 팔로우 상태인 경우
        if was_accepted:
            Member.objects.filter(id=member.id).update(following_count=F('following_count') - 1)
            Member.objects.filter(id=following.id).update(follower_count=F('follower_count') - 1)
            response = SuccessResponseBuilder().with_message("팔로우 취소 성공").build()
            return Response(response, status=status.HTTP_200_OK)

        # 팔로우 요청 상태인 경우
        response = SuccessResponseBuilder().with_message("팔로우 요청 취소 성공").build()
        return Response(response, status=status.HTTP_200_OK)


# Block APIView
class BlockAPIView(APIView):
    permission_classes = [IsSelf]

    # 차단 목록 조회
    @extend_schema(**BlockSchema.get_blocks())
    def get(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        blocked = member.followings.filter(status=FollowStatus.BLOCKED)
        serializer = FollowSerializer(blocked, many=True)
        response = SuccessResponseBuilder().with_message("차단 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Block Detail APIView
class BlockDetailAPIView(APIView):
    permission_classes = [IsSelf]

    # 차단 추가
    @extend_schema(**BlockSchema.create_block())
    def post(self, request, member_id, block_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        block = get_object_or_404(Member, id=block_id)

        # 차단 하려는 대상이 자기 자신인 경우
        if member == block:
            response = ErrorResponseBuilder().with_message("자기 자신을 차단할 수 없습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            my_follow = Follow.objects.filter(follower=member, following=block).first()

            # 1. 내가 팔로우 상태인 경우
            if my_follow and my_follow.status == FollowStatus.ACCEPTED:
                Member.objects.filter(id=member.id).update(following_count=F('following_count') - 1)
                Member.objects.filter(id=block.id).update(follower_count=F('follower_count') - 1)

            # 2. 내가 팔로우 또는 팔로우 요청 상태인 경우
            if my_follow:
                my_follow.status = FollowStatus.BLOCKED
                my_follow.save(update_fields=["status"])
                follow = my_follow

            # 3. 내가 팔로우 요청 상태가 아닌 경우
            else:
                follow = Follow.objects.create(follower=member, following=block, status=FollowStatus.BLOCKED)

            reverse_follow = Follow.objects.filter(follower=block, following=member).first()

            # 1. 상대방이 나를 팔로우 상태인 경우
            if reverse_follow and reverse_follow.status == FollowStatus.ACCEPTED:
                Member.objects.filter(id=member.id).update(follower_count=F('follower_count') - 1)
                Member.objects.filter(id=block.id).update(following_count=F('following_count') - 1)

            # 2. 상대방이 나를 팔로우 또는 팔로우 요청 상태인 경우
            if reverse_follow:
                reverse_follow.delete()

        serializer = FollowSerializer(follow)
        response = SuccessResponseBuilder().with_message("차단 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # 차단 해제
    @extend_schema(**BlockSchema.delete_block())
    def delete(self, request, member_id, block_id):
        member = get_object_or_404(Member, id=member_id)
        self.check_object_permissions(request, member)
        block = get_object_or_404(Member, id=block_id)

        deleted, _ = member.followings.filter(following=block, status=FollowStatus.BLOCKED).delete()
        if deleted:
            response = SuccessResponseBuilder().with_message("차단 해제 성공").build()
            return Response(response, status=status.HTTP_200_OK)
        response = ErrorResponseBuilder().with_message("차단되지 않았습니다.").build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Post Category
# <-------------------------------------------------------------------------------------------------------------------------------->
# Post Category APIView
class PostCategoryAPIView(APIView):
    permission_classes = [IsMember]
    
    # Post Category 목록 조회: 멤버만 가능
    @extend_schema(**PostCategorySchema.get_categories())
    def get(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        categories = community.post_categories.all().select_related('parent').order_by('id')
        serializer = PostCategorySerializer(categories, many=True)
        response = SuccessResponseBuilder().with_message("카테고리 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Post Category Detail APIView
class PostCategoryDetailAPIView(APIView):
    permission_classes = [IsMember]

    # Post Category 상세 조회: 멤버만 가능
    @extend_schema(**PostCategorySchema.get_category_detail())
    def get(self, request, category_id):
        category = get_object_with_permission(self, PostCategory, category_id, request)
        serializer = PostCategorySerializer(category)
        response = SuccessResponseBuilder().with_message("카테고리 상세 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Favorite Post Category APIView
class FavoritePostCategoryAPIView(APIView):
    permission_classes = [IsMember]
    
    # Post Category 즐겨찾기 여부 조회: 멤버이면서 본인만 가능
    @extend_schema(**PostCategorySchema.get_favorite_status())
    def get(self, request, category_id):
        category = get_object_with_permission(self, PostCategory, category_id, request)
        favored = PostCategoryFavorite.objects.filter(member=category._member, category=category).exists()
        response = SuccessResponseBuilder().with_message("카테고리 즐겨찾기 여부 조회 성공").with_data({'favored': favored}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Category 즐겨찾기: 멤버이면서 본인만 가능
    @extend_schema(**PostCategorySchema.create_favorite())
    def post(self, request, category_id):
        category = get_object_with_permission(self, PostCategory, category_id, request)
        member = get_member_from_obj(category)
        post_category_favorite, created = PostCategoryFavorite.objects.get_or_create(member=member, category=category)
        if created:
            increase_count(post_category_favorite)
        response = SuccessResponseBuilder().with_message("카테고리 즐겨찾기 성공").with_data({'favored': True}).build()
        return Response(response, status=status.HTTP_201_CREATED)

    # Post Category 즐겨찾기 취소: 멤버이면서 본인만 가능
    @extend_schema(**PostCategorySchema.delete_favorite())
    def delete(self, request, category_id):
        category = get_object_with_permission(self, PostCategory, category_id, request)
        member = get_member_from_obj(category)
        post_category_favorite = PostCategoryFavorite.objects.filter(member=member, category=category).first()
        if post_category_favorite:
            decrease_count(post_category_favorite)
            post_category_favorite.delete()
        response = SuccessResponseBuilder().with_message("카테고리 즐겨찾기 취소 성공").with_data({'favored': False}).build()
        return Response(response, status=status.HTTP_200_OK)


# Favorite Post Category List API View
class FavoritePostCategoryListAPIView(APIView):
    permission_classes = [IsMember]

    # 커뮤니티 내 즐겨찾기 한 카테고리 목록
    @extend_schema(**PostCategorySchema.get_categories())
    def get(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        member = get_member_from_obj(community)
        favorites = PostCategoryFavorite.objects.filter(member=member, category__community=community).select_related('category')
        categories = [fav.category for fav in favorites]
        serializer = PostCategorySerializer(categories, many=True)
        response = SuccessResponseBuilder().with_message("커뮤니티 내 즐겨찾기 한 카테고리 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Post
# <-------------------------------------------------------------------------------------------------------------------------------->
# Post APIView
class PostAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostPagination

    # Post 목록 조회: 멤버만 가능
    @extend_schema(**PostSchema.get_posts())
    def get(self, request, category_id):
        category = get_object_with_permission(self, PostCategory, category_id, request)
        member = get_member_from_obj(category)
        blocked_member_ids = get_blocked_member_ids([member])

        if category.parent is None:
            subcategory_ids = category.post_subcategories.values_list('id', flat=True)
            posts = Post.objects.filter(category__in=[category.id, *subcategory_ids])
        else:
            posts = category.posts.all()
            
        posts = posts.exclude(author_id__in=blocked_member_ids).select_related('author').annotate(
            is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), member=member)),
            is_scraped=Exists(PostScrap.objects.filter(post=OuterRef('pk'), member=member)),
            is_following=Exists(Follow.objects.filter(follower=member, following=OuterRef('author'), status=FollowStatus.ACCEPTED)),
        ).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)
        
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("카테고리 내 글 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)

        serializer = PostListSerializer(posts, many=True)
        response = SuccessResponseBuilder().with_message("카테고리 내 글 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post 작성: 멤버만 가능
    @extend_schema(**PostSchema.create_post())
    def post(self, request, category_id):
        category = get_object_with_permission(self, PostCategory, category_id, request)
        member = get_member_from_obj(category)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(category=category, author=member)
            increase_count(post)
            response = SuccessResponseBuilder().with_message("글 작성 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_201_CREATED)

        response = ErrorResponseBuilder().with_message("글 작성 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Post by Community API View
class PostByCommunityAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostPagination

    # Post 목록 조회: 멤버만 가능
    @extend_schema(**PostSchema.get_posts_by_community())
    def get(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        member = get_member_from_obj(community)
        blocked_member_ids = get_blocked_member_ids([member])

        posts = Post.objects.filter(is_active=True, category__community=community).exclude(author_id__in=blocked_member_ids).select_related('author', 'category', 'category__community').annotate(
            is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), member=member)),
            is_scraped=Exists(PostScrap.objects.filter(post=OuterRef('pk'), member=member)),
            is_following=Exists(Follow.objects.filter(follower=member, following=OuterRef('author'), status=FollowStatus.ACCEPTED)),
        ).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)
        
        serializer = PostListSerializer(posts, many=True)
        response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)
    

# Post by Member API View
class PostByMemberAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostPagination

    @extend_schema(**PostSchema.get_posts_by_member())
    def get(self, request):
        members = Member.objects.filter(user=request.user)
        community_ids = members.values_list('community_id', flat=True)
        blocked_member_ids = get_blocked_member_ids(members)

        posts = Post.objects.filter(category__community__in=community_ids).exclude(author_id__in=blocked_member_ids).select_related('author', 'category', 'category__community').annotate(
            is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), member__user=request.user, member__community=OuterRef('category__community'))),
            is_scraped=Exists(PostScrap.objects.filter(post=OuterRef('pk'), member__user=request.user, member__community=OuterRef('category__community'))),
            is_following=Exists(Follow.objects.filter(follower__user=request.user, follower__community=OuterRef('category__community'), following=OuterRef('author'), status=FollowStatus.ACCEPTED)),
        ).distinct().order_by('-id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)

        if page is not None:
            serializer = PostListSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)
        
        serializer = PostListSerializer(posts, many=True)
        response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Post by Favorite Community API View
class PostByFavoriteCommunityAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostPagination

    # 즐겨찾는 커뮤니티의 Post 목록 조회: 멤버만 가능
    @extend_schema(**PostSchema.get_posts_by_favorite_community())
    def get(self, request):
        members = Member.objects.filter(user=request.user)
        blocked_member_ids = get_blocked_member_ids(members)
        favorite_community_ids = CommunityFavorite.objects.filter(member__in=members).values_list('community_id', flat=True)

        posts = Post.objects.filter(category__community__in=favorite_community_ids).exclude(author_id__in=blocked_member_ids).select_related('author', 'category', 'category__community').annotate(
            is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), member__user=request.user, member__community=OuterRef('category__community'))),
            is_scraped=Exists(PostScrap.objects.filter(post=OuterRef('pk'), member__user=request.user, member__community=OuterRef('category__community'))),
            is_following=Exists(Follow.objects.filter(follower__user=request.user, follower__community=OuterRef('category__community'), following=OuterRef('author'), status=FollowStatus.ACCEPTED)),
        ).distinct().order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)
        
        serializer = PostListSerializer(posts, many=True)
        response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Post by Favorite Category in Community API View
class PostByFavoriteCategoryAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostPagination

    # 즐겨찾는 카테고리의 Post 목록 조회: 본인만 가능
    @extend_schema(**PostSchema.get_posts_by_favorite_category())
    def get(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        member = get_member_from_obj(community)
        blocked_member_ids = get_blocked_member_ids([member])
        favorite_category_ids = PostCategoryFavorite.objects.filter(member=member, category__community=community).values_list('category_id', flat=True)
        posts = Post.objects.filter(category_id__in=favorite_category_ids, category__community=community).exclude(author_id__in=blocked_member_ids).select_related('author', 'category', 'category__community').annotate(
            is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), member=member)),
            is_scraped=Exists(PostScrap.objects.filter(post=OuterRef('pk'), member=member)),
            is_following=Exists(Follow.objects.filter(follower=member, following=OuterRef('author'), status=FollowStatus.ACCEPTED)),
        ).distinct().order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)
        
        serializer = PostListSerializer(posts, many=True)
        response = SuccessResponseBuilder().with_message("커뮤니티 내 글 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)


# Post Detail APIView
class PostDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsMember()]
        else :
            return [IsMemberAuthor()]

    # Post 상세 조회: 멤버만 가능
    @extend_schema(**PostSchema.get_post_detail())
    def get(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request, queryset=Post.objects.select_related('author', 'category', 'category__community'))
        member = get_member_from_obj(post)
        blocked_member_ids = get_blocked_member_ids([member])
        if post.author_id in blocked_member_ids:
            response = ErrorResponseBuilder().with_message("Post 상세 조회 실패").with_errors({'detail': '차단된 멤버입니다.'}).build()
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        post.is_liked = PostLike.objects.filter(post=post, member=member).exists()
        post.is_scraped = PostScrap.objects.filter(post=post, member=member).exists()
        post.is_following = Follow.objects.filter(follower=member, following=post.author, status=FollowStatus.ACCEPTED).exists()
        serializer = PostDetailSerializer(post)
        response = SuccessResponseBuilder().with_message("Post 상세 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post 수정: 멤버이면서 작성자만 가능
    @extend_schema(**PostSchema.update_post())
    def put(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = SuccessResponseBuilder().with_message("Post 수정 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_200_OK)

        response = ErrorResponseBuilder().with_message("Post 수정 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # Post 삭제: 멤버이면서 작성자만 가능
    @extend_schema(**PostSchema.delete_post())
    def delete(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        member = get_member_from_obj(post)
        decrease_count(post)
        post.delete()
        response = SuccessResponseBuilder().with_message("Post 삭제 성공").build()
        return Response(response, status=status.HTTP_200_OK)


# Post Like APIView
class PostLikeAPIView(APIView):
    permission_classes = [IsMember]
    
    # Post 좋아요 여부 조회: 멤버이면서 본인만 가능
    @extend_schema(**PostSchema.get_like_status())
    def get(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        member = get_member_from_obj(post)
        liked = PostLike.objects.filter(member=member, post=post).exists()
        response = SuccessResponseBuilder().with_message("Post 좋아요 여부 조회 성공").with_data({'liked': liked}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post 좋아요: 멤버이면서 본인만 가능
    @extend_schema(**PostSchema.create_like())
    def post(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        member = get_member_from_obj(post)
        post_like, created = PostLike.objects.get_or_create(member=member, post=post)
        if created:
            increase_count(post_like)
        response = SuccessResponseBuilder().with_message("Post 좋아요 성공").with_data({'liked': True}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post 좋아요 취소: 멤버이면서 본인만 가능
    @extend_schema(**PostSchema.delete_like())
    def delete(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        member = get_member_from_obj(post)
        post_like = PostLike.objects.filter(member=member, post=post).first()
        if post_like:
            decrease_count(post_like)
            post_like.delete()
        response = SuccessResponseBuilder().with_message("Post 좋아요 취소 성공").with_data({'liked': False}).build()
        return Response(response, status=status.HTTP_200_OK)


# Post Scrap APIView
class PostScrapAPIView(APIView):
    permission_classes = [IsMember]

    # Post 스크랩 여부 조회: 멤버이면서 본인만 가능
    @extend_schema(**PostSchema.get_scrap_status())
    def get(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        scraped = PostScrap.objects.filter(member=post._member, post=post).exists()
        response = SuccessResponseBuilder().with_message("Post 스크랩 여부 조회 성공").with_data({'scraped': scraped}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post 스크랩: 멤버이면서 본인만 가능
    @extend_schema(**PostSchema.create_scrap())
    def post(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        post_scrap, created = PostScrap.objects.get_or_create(member=post._member, post=post)
        if created:
            increase_count(post_scrap)
        response = SuccessResponseBuilder().with_message("Post 스크랩 성공").with_data({'scraped': True}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post 스크랩 취소: 멤버이면서 본인만 가능
    @extend_schema(**PostSchema.delete_scrap())
    def delete(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        post_scrap = PostScrap.objects.filter(member=post._member, post=post).first()
        if post_scrap:
            decrease_count(post_scrap)
            post_scrap.delete()
        response = SuccessResponseBuilder().with_message("Post 스크랩 취소 성공").with_data({'scraped': False}).build()
        return Response(response, status=status.HTTP_200_OK)


# Post Comment
# <-------------------------------------------------------------------------------------------------------------------------------->
# Post Comment APIView
class PostCommentAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostCommentPagination

    # Post Comment 목록 조회: 멤버만 가능
    @extend_schema(**PostCommentSchema.get_comments())
    def get(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request, queryset=Post.objects.select_related('author'))
        member = get_member_from_obj(post)
        blocked_member_ids = get_blocked_member_ids([member])
        comments = post.post_comments.all().exclude(author_id__in=blocked_member_ids).annotate(
            is_liked=Exists(PostCommentLike.objects.filter(comment=OuterRef('pk'), member=member)),
        ).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = PostCommentSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("Post Comment 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)

        serializer = PostCommentSerializer(comments, many=True)
        response = SuccessResponseBuilder().with_message("Post Comment 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)
    
    # Post Comment 작성: 멤버만 가능
    @extend_schema(**PostCommentSchema.create_comment())
    def post(self, request, post_id):
        post = get_object_with_permission(self, Post, post_id, request)
        member = get_member_from_obj(post)
        serializer = PostCommentSerializer(data=request.data)
        if serializer.is_valid():
            post_comment = serializer.save(author=member, post=post)
            increase_count(post_comment)
            response = SuccessResponseBuilder().with_message("Post Comment 작성 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_201_CREATED)

        response = ErrorResponseBuilder().with_message("Post Comment 작성 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Post Comment Detail APIView
class PostCommentDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsMember()]
        else :
            return [IsMemberAuthor()]

    # Post Comment 상세 조회: 멤버만 가능
    @extend_schema(**PostCommentSchema.get_comment_detail())
    def get(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        member = get_member_from_obj(comment)
        blocked_member_ids = get_blocked_member_ids([member])
        if comment.author_id in blocked_member_ids:
            response = ErrorResponseBuilder().with_message("Post Comment 상세 조회 실패").with_errors({'detail': '차단된 멤버입니다.'}).build()
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        comment.is_liked = PostCommentLike.objects.filter(comment=comment, member=member).exists()
        serializer = PostCommentSerializer(comment)
        response = SuccessResponseBuilder().with_message("Post Comment 상세 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Comment 수정: 멤버이면서 작성자만 가능
    @extend_schema(**PostCommentSchema.update_comment())
    def put(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        serializer = PostCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = SuccessResponseBuilder().with_message("Post Comment 수정 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_200_OK)
        
        response = ErrorResponseBuilder().with_message("Post Comment 수정 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # Post Comment 삭제: 멤버이면서 작성자만 가능
    @extend_schema(**PostCommentSchema.delete_comment())
    def delete(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        has_replies = comment.post_replies.exists()
        decrease_count(comment)
        if has_replies:
            comment.soft_delete()   # Soft delete (대댓글이 있으면 실제 삭제하지 않음)
        else:
            comment.delete()        # 대댓글이 없으면 실제 삭제
        response = SuccessResponseBuilder().with_message("Post Comment 삭제 성공").build()
        return Response(response, status=status.HTTP_200_OK)


# Post Comment Like APIView
class PostCommentLikeAPIView(APIView):
    permission_classes = [IsMember]

    # Post Comment 좋아요 여부 조회: 멤버이면서 본인만 가능
    @extend_schema(**PostCommentSchema.get_like_status())
    def get(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        liked = PostCommentLike.objects.filter(member=comment._member, comment=comment).exists()
        response = SuccessResponseBuilder().with_message("Post Comment 좋아요 여부 조회 성공").with_data({'liked': liked}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Comment 좋아요: 멤버이면서 본인만 가능
    @extend_schema(**PostCommentSchema.create_like())
    def post(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        member = get_member_from_obj(comment)
        post_comment_like, created = PostCommentLike.objects.get_or_create(member=member, comment=comment)
        if created:
            increase_count(post_comment_like)
        response = SuccessResponseBuilder().with_message("Post Comment 좋아요 성공").with_data({'liked': True}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Comment 좋아요 취소: 멤버이면서 본인만 가능
    @extend_schema(**PostCommentSchema.delete_like())
    def delete(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        member = get_member_from_obj(comment)
        post_comment_like = PostCommentLike.objects.filter(member=member, comment=comment).first()
        if post_comment_like:
            decrease_count(post_comment_like)
            post_comment_like.delete()
        response = SuccessResponseBuilder().with_message("Post Comment 좋아요 취소 성공").with_data({'liked': False}).build()
        return Response(response, status=status.HTTP_200_OK)


# Post Reply
# <-------------------------------------------------------------------------------------------------------------------------------->
# Post Reply APIView
class PostReplyAPIView(APIView):
    permission_classes = [IsMember]
    pagination_class = PostReplyPagination

    # Post Reply 목록 조회: 멤버만 가능
    @extend_schema(**PostReplySchema.get_replies())
    def get(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        member = get_member_from_obj(comment)
        blocked_member_ids = get_blocked_member_ids([member])
        replies = comment.post_replies.all().exclude(author_id__in=blocked_member_ids).order_by('-id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(replies, request)

        if page is not None:
            serializer = PostReplySerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("Post Reply 목록 조회 성공").with_data(serializer.data).with_page_pagination(paginator, page).build()
            return Response(response, status=status.HTTP_200_OK)

        serializer = PostReplySerializer(replies, many=True)
        response = SuccessResponseBuilder().with_message("Post Reply 목록 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Reply 작성: 멤버만 가능
    @extend_schema(**PostReplySchema.create_reply())
    def post(self, request, comment_id):
        comment = get_object_with_permission(self, PostComment, comment_id, request)
        member = get_member_from_obj(comment)
        serializer = PostReplySerializer(data=request.data)
        if serializer.is_valid():
            post_reply = serializer.save(comment=comment, author=member)
            increase_count(post_reply)
            response = SuccessResponseBuilder().with_message("Post Reply 작성 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_201_CREATED)

        response = ErrorResponseBuilder().with_message("Post Reply 작성 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Post Reply Detail APIView
class PostReplyDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsMember()]
        else :
            return [IsMemberAuthor()]

    # Post Reply 상세 조회: 멤버만 가능
    @extend_schema(**PostReplySchema.get_reply_detail())
    def get(self, request, reply_id):
        reply = get_object_with_permission(self, PostReply, reply_id, request)
        member = get_member_from_obj(reply)
        blocked_member_ids = get_blocked_member_ids([member])
        if reply.author_id in blocked_member_ids:
            response = ErrorResponseBuilder().with_message("Post Reply 상세 조회 실패").with_errors({'detail': '차단된 멤버입니다.'}).build()
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        reply.is_liked = PostReplyLike.objects.filter(reply=reply, member=member).exists()
        serializer = PostReplySerializer(reply)
        response = SuccessResponseBuilder().with_message("Post Reply 상세 조회 성공").with_data(serializer.data).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Reply 수정: 멤버이면서 작성자만 가능
    @extend_schema(**PostReplySchema.update_reply())
    def put(self, request, reply_id):
        reply = get_object_with_permission(self, PostReply, reply_id, request)
        serializer = PostReplySerializer(reply, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = SuccessResponseBuilder().with_message("Post Reply 수정 성공").with_data(serializer.data).build()
            return Response(response, status=status.HTTP_200_OK)

        response = ErrorResponseBuilder().with_message("Post Reply 수정 실패").with_errors(serializer.errors).build()
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # Post Reply 삭제: 멤버이면서 작성자만 가능
    @extend_schema(**PostReplySchema.delete_reply())
    def delete(self, request, reply_id):
        reply = get_object_with_permission(self, PostReply, reply_id, request)
        decrease_count(reply)
        reply.delete()
        response = SuccessResponseBuilder().with_message("Post Reply 삭제 성공").build()
        return Response(response, status=status.HTTP_200_OK)


# Post Reply Like APIView
class PostReplyLikeAPIView(APIView):
    permission_classes = [IsMember]

    # Post Reply 좋아요 여부 조회: 멤버이면서 본인만 가능
    @extend_schema(**PostReplySchema.get_like_status())
    def get(self, request, reply_id):
        reply = get_object_with_permission(self, PostReply, reply_id, request)
        liked = PostReplyLike.objects.filter(member=reply._member, reply=reply).exists()
        response = SuccessResponseBuilder().with_message("Post Reply 좋아요 여부 조회 성공").with_data({'liked': liked}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Reply 좋아요: 멤버이면서 본인만 가능
    @extend_schema(**PostReplySchema.create_like())
    def post(self, request, reply_id):
        reply = get_object_with_permission(self, PostReply, reply_id, request)
        member = get_member_from_obj(reply)
        post_reply_like, created = PostReplyLike.objects.get_or_create(member=member, reply=reply)
        if created:
            increase_count(post_reply_like)
        response = SuccessResponseBuilder().with_message("Post Reply 좋아요 성공").with_data({'liked': True}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Post Reply 좋아요 취소: 멤버이면서 본인만 가능
    @extend_schema(**PostReplySchema.delete_like())
    def delete(self, request, reply_id):
        reply = get_object_with_permission(self, PostReply, reply_id, request)
        member = get_member_from_obj(reply)
        post_reply_like = PostReplyLike.objects.filter(member=member, reply=reply).first()
        if post_reply_like:
            decrease_count(post_reply_like)
            post_reply_like.delete()
        response = SuccessResponseBuilder().with_message("Post Reply 좋아요 취소 성공").with_data({'liked': False}).build()
        return Response(response, status=status.HTTP_200_OK)