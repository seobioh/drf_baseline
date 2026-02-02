# communities/urls.py
app_name = 'communities'

from django.contrib import admin
from django.urls import path

from .views import CommunityAPIView, FavoriteCommunityListAPIView, CommunityDetailAPIView, FavoriteCommunityAPIView
from .views import MemberAPIView, MemberListAPIView, MemberDetailAPIView
from .views import FollowerAPIView, FollowerDetailAPIView, FollowingAPIView,FollowingDetailAPIView, BlockAPIView, BlockDetailAPIView

urlpatterns = [
    # Community
    # <-------------------------------------------------------------------------------------------------------------------------------->
    path('', CommunityAPIView.as_view()),                                           # 커뮤니티 목록
    path('/favorites', FavoriteCommunityListAPIView.as_view()),                     # 내가 즐겨찾는 커뮤니티 목록
    path('/<int:community_id>', CommunityDetailAPIView.as_view()),                  # 커뮤니티 상세 보기
    path('/<int:community_id>/members', MemberAPIView.as_view()),                   # 커뮤니티 멤버 목록 보기    
    path('/<int:community_id>/favorites', FavoriteCommunityAPIView.as_view()),      # 커뮤니티 즐겨찾기 관리 (GET, POST, DELETE)

    # Member
    # <-------------------------------------------------------------------------------------------------------------------------------->
    path('/members', MemberListAPIView.as_view()),                                                      # 내가 속한 커뮤니티 목록
    path('/members/<int:member_id>', MemberDetailAPIView.as_view()),                                    # 멤버 관리 (GET, PUT, DELETE)
    path('/members/<int:member_id>/followers', FollowerAPIView.as_view()),                              # 멤버 팔로워 목록
    path('/members/<int:member_id>/followers/<int:follower_id>', FollowerDetailAPIView.as_view()),      # 멤버 팔로워 관리 (수락, 삭제)
    path('/members/<int:member_id>/followings', FollowingAPIView.as_view()),                            # 멤버 팔로잉 목록
    path('/members/<int:member_id>/followings/<int:following_id>', FollowingDetailAPIView.as_view()),   # 멤버 팔로잉 관리 (요청, 취소)
    path('/members/<int:member_id>/blocks', BlockAPIView.as_view()),                                    # 멤버 차단 목록
    path('/members/<int:member_id>/blocks/<int:block_id>', BlockDetailAPIView.as_view()),               # 멤버 차단 관리 (추가, 삭제)
]