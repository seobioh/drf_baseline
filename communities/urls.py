# communities/urls.py
app_name = 'communities'

from django.contrib import admin
from django.urls import path

from .views import CommunityAPIView, FavoriteCommunityListAPIView, CommunityDetailAPIView, FavoriteCommunityAPIView
from .views import MemberAPIView, MemberListAPIView, MemberDetailAPIView
from .views import FollowerAPIView, FollowerDetailAPIView, FollowingAPIView,FollowingDetailAPIView, BlockAPIView, BlockDetailAPIView
from .views import PostByCommunityAPIView, PostByMemberAPIView, PostByFavoriteCommunityAPIView, PostByFavoriteCategoryAPIView, PostCategoryAPIView
from .views import PostAPIView, FavoritePostCategoryAPIView, FavoritePostCategoryListAPIView, PostDetailAPIView, PostLikeAPIView, PostScrapAPIView
from .views import PostCommentAPIView, PostCommentDetailAPIView, PostCommentLikeAPIView, PostReplyAPIView, PostReplyDetailAPIView, PostReplyLikeAPIView

urlpatterns = [
    # Community
    # <-------------------------------------------------------------------------------------------------------------------------------->
    path('', CommunityAPIView.as_view()),                                           # 커뮤니티 목록
    path('/favorites', FavoriteCommunityListAPIView.as_view()),                     # 내가 즐겨찾는 커뮤니티 목록
    path('/favorites/posts', PostByFavoriteCommunityAPIView.as_view()),             # 즐겨찾기 한 커뮤니티 내 글 목록
    path('/<int:community_id>', CommunityDetailAPIView.as_view()),                  # 커뮤니티 상세 보기
    path('/<int:community_id>/members', MemberAPIView.as_view()),                   # 커뮤니티 멤버 목록 보기    
    path('/<int:community_id>/favorites', FavoriteCommunityAPIView.as_view()),      # 커뮤니티 즐겨찾기 관리 (GET, POST, DELETE)
    path('/<int:community_id>/categories', PostCategoryAPIView.as_view()),                  # 커뮤니티 내 카테고리 목록
    path('/<int:community_id>/categories/favorites', FavoritePostCategoryListAPIView.as_view()),       # 커뮤니티 내 즐겨찾기 한 카테고리 목록
    path('/<int:community_id>/categories/favorites/posts', PostByFavoriteCategoryAPIView.as_view()),         # 커뮤니티 내 즐겨찾기 한 카테고리 내 글 목록

    path('/<int:community_id>/posts', PostByCommunityAPIView.as_view()),                          # 커뮤니티 내 전체 글 목록
    #path('/<int:community_id>/posts/popular', PopularPostByCommunityAPIView.as_view()),           # 커뮤니티 내 인기글 목록
    #path('/<int:community_id>/posts/mine', MyPostByCommunityAPIView.as_view()),                   # 커뮤니티 내 내가 작성한 글 목록              
    #path('/<int:community_id>/posts/liked', LikedPostByCommunityAPIView.as_view()),               # 커뮤니티 내 내가 좋아요 한 글 목록
    #path('/<int:community_id>/posts/scraped', ScrapedPostByCommunityAPIView.as_view()),           # 커뮤니티 내 내가 스크랩 한 글 목록
    #path('/<int:community_id>/posts/commented', CommentedPostByCommunityAPIView.as_view()),       # 커뮤니티 내 내가 댓글 단 글 목록
    #path('/<int:community_id>/posts/replied', RepliedPostByCommunityAPIView.as_view()),           # 커뮤니티 내 내가 답글 단 글 목록

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

    # Post
    # <-------------------------------------------------------------------------------------------------------------------------------->
    #path('/categories/<int:category_id>', PostCategoryDetailAPIView.as_view()),              # 카테고리 상세 관리 (GET)
    path('/categories/<int:category_id>/posts', PostAPIView.as_view()),                       # 카테고리 내 글 관리 (GET, POST)
    path('/categories/<int:category_id>/favorites', FavoritePostCategoryAPIView.as_view()),   # 즐겨찾는 카테고리 관리 (GET, POST, DELETE)

    path('/posts', PostByMemberAPIView.as_view()),                                # 내가 속한 커뮤니티의 전체 글 목록
    #path('/posts/popular', PopularPostAPIView.as_view()),                         # 인기 글 목록
    #path('/posts/mine', MyPostAPIView.as_view()),                                 # 내가 쓴 글 목록
    #path('/posts/liked', LikedPostAPIView.as_view()),                             # 내가 좋아요 누른 글 목록
    #path('/posts/scraped', ScrapedPostAPIView.as_view()),                         # 내가 스크랩 한 누른 글 목록
    #path('/posts/commented', CommentedPostAPIView.as_view()),                     # 내가 댓글 단 글 목록
    #path('/posts/replied', RepliedPostAPIView.as_view()),                         # 내가 답글 단 글 목록
    path('/posts/<int:post_id>', PostDetailAPIView.as_view()),                            # 글 상세 관리 (GET, PUT, DELETE)
    path('/posts/<int:post_id>/likes', PostLikeAPIView.as_view()),                        # 글 좋아요 관리 (GET, POST, DELETE)
    path('/posts/<int:post_id>/scraps', PostScrapAPIView.as_view()),                      # 글 스크랩 관리 (GET, POST, DELETE)
    path('/posts/<int:post_id>/comments', PostCommentAPIView.as_view()),                  # 글 댓글 관리 (GET, POST)

    path('/comments/<int:comment_id>', PostCommentDetailAPIView.as_view()),         # 글 댓글 상세 관리 (GET, PUT, DELETE)
    path('/comments/<int:comment_id>/likes', PostCommentLikeAPIView.as_view()),     # 글 댓글 좋아요 관리 (GET, POST, DELETE)
    path('/comments/<int:comment_id>/replies', PostReplyAPIView.as_view()),         # 글 답글 관리 (GET, POST)

    path('/replies/<int:reply_id>', PostReplyDetailAPIView.as_view()),              # 글 답글 상세 관리 (GET, PUT, DELETE)
    path('/replies/<int:reply_id>/likes', PostReplyLikeAPIView.as_view()),          # 글 답글 좋아요 관리 (GET, POST, DELETE)
]