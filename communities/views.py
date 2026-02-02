# communities/views.py
app_name = 'communities'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db import transaction
from django.db.models import Q, F
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from server.utils import SuccessResponseBuilder, ErrorResponseBuilder

from .utils import get_object_with_permission, get_member_from_obj
from .models import Community, CommunityFavorite, Member, Follow, FollowStatus
from .paginations import FollowerCursorPagination, FollowingCursorPagination
from .schemas import CommunitySchema, MemberSchema, FollowerSchema, FollowingSchema, BlockSchema
from .serializers import CommunitySerializer, MemberSerializer, MemberListSerializer, MemberSimpleSerializer, FollowSerializer
from .permissions import AllowAny, IsAuthenticated, IsSelf, IsProfileReadable

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
        favored = CommunityFavorite.objects.filter(member=get_member_from_obj(community)).exists()
        response = SuccessResponseBuilder().with_message("커뮤니티 즐겨찾기 여부 조회 성공").with_data({"favored": favored}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Community 즐겨찾기: 멤버이면서 본인만 가능
    @extend_schema(**CommunitySchema.create_favorite())
    def post(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        obj, created = CommunityFavorite.objects.get_or_create(member=get_member_from_obj(community), community=community)
        if created:
            Community.objects.filter(id=community_id).update(favorite_count=F('favorite_count') + 1)
        response = SuccessResponseBuilder().with_message("커뮤니티 즐겨찾기 성공").with_data({"favored": True}).build()
        return Response(response, status=status.HTTP_200_OK)

    # Community 즐겨찾기 취소: 멤버이면서 본인만 가능
    @extend_schema(**CommunitySchema.delete_favorite())
    def delete(self, request, community_id):
        community = get_object_with_permission(self, Community, community_id, request)
        deleted, _ = CommunityFavorite.objects.filter(member=get_member_from_obj(community), community=community).delete()
        if deleted:
            Community.objects.filter(id=community_id).update(favorite_count=F('favorite_count') - 1)
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
            serializer.save(community=community, user=request.user, is_staff=request.user.is_staff, is_admin=request.user.is_admin)
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
            pagination = {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'page_size': paginator.page_size,
            }
            serializer = FollowSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("팔로워 목록 조회 성공").with_data({"followers": serializer.data, "pagination": pagination}).build()

        serializer = FollowSerializer(followers, many=True)
        response = SuccessResponseBuilder().with_message("팔로워 목록 조회 성공").with_data({"followers": serializer.data}).build()
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
            pagination = {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'page_size': paginator.page_size,
            }
            serializer = FollowSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("팔로잉 목록 조회 성공").with_data({"followings": serializer.data, "pagination": pagination}).build()

        serializer = FollowSerializer(followings, many=True)
        response = SuccessResponseBuilder().with_message("팔로잉 목록 조회 성공").with_data({"followings": serializer.data}).build()
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
        response = SuccessResponseBuilder().with_message("팔로우 성공").build()
        Member.objects.filter(id=member.id).update(following_count=F('following_count') + 1)
        Member.objects.filter(id=following.id).update(follower_count=F('follower_count') + 1)
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