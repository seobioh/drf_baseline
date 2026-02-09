# communities/schemas.py
app_name = "communities"

from rest_framework import serializers

from drf_spectacular.utils import OpenApiExample

from server.schemas import SuccessResponseSerializer, ErrorResponseSerializer


# Wrapper Serializers
# <-------------------------------------------------------------------------------------------------------------------------------->
# Request Serializers
class MemberRequestSerializer(serializers.Serializer):
    nickname = serializers.CharField(required=False, allow_blank=True, max_length=24, help_text="닉네임 (선택, 없으면 자동 생성)")
    profile_image = serializers.CharField(required=False, allow_blank=True, max_length=255, help_text="프로필 이미지 URL")


class PostRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, help_text="글 제목")
    content = serializers.CharField(help_text="글 내용")
    images = serializers.JSONField(required=False, allow_null=True, help_text="이미지 URL 배열 (선택)")
    is_anonymous = serializers.BooleanField(required=False, default=False, help_text="익명 여부 (선택, 기본값: False)")


class PostCommentRequestSerializer(serializers.Serializer):
    content = serializers.CharField(help_text="댓글 내용")
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255, help_text="이미지 URL (선택)")


class PostReplyRequestSerializer(serializers.Serializer):
    content = serializers.CharField(help_text="대댓글 내용")
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255, help_text="이미지 URL (선택)")


# Common Examples
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommonExamples:
    @staticmethod
    def success_example(message="요청이 성공적으로 처리되었습니다.", data=None):
        if data is None:
            data = {"result": "success"}
        
        return OpenApiExample(
            "Success Response",
            summary="성공",
            description="요청이 성공적으로 처리된 경우의 응답",
            value={
                "code": 0,
                "message": message,
                "data": data
            },
            response_only=True,
            status_codes=['200']
        )
    
    @staticmethod
    def error_example(message="요청 처리 중 오류가 발생했습니다.", errors=None):
        if errors is None:
            errors = {"detail": "요청을 처리할 수 없습니다."}
        
        return OpenApiExample(
            "Error Response",
            summary="실패",
            description="요청 처리 중 오류가 발생한 경우의 응답",
            value={
                "code": 1,
                "message": message,
                "errors": errors
            },
            response_only=True,
            status_codes=['400', '500']
        )


# Community Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommunitySchema:
    @staticmethod
    def get_communities():
        return {
            'summary': "커뮤니티 목록 조회",
            'description': "모든 커뮤니티 목록을 조회합니다. 누구나 조회 가능합니다.",
            'operation_id': 'communities_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 목록 조회 성공",
                    data={
                        "communities": [
                            {
                                "id": 1,
                                "name": "커뮤니티 이름",
                                "description": "커뮤니티 설명",
                                "image": "https://example.com/image.jpg",
                                "member_count": 100,
                                "favorite_count": 50,
                                "post_count": 200,
                                "score": 1000,
                                "is_active": True,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                )
            ]
        }
    
    @staticmethod
    def get_community_detail():
        return {
            'summary': "커뮤니티 상세 조회",
            'description': "특정 커뮤니티의 상세 정보를 조회합니다. 누구나 조회 가능합니다.",
            'operation_id': 'communities_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 상세 조회 성공",
                    data={
                        "community": {
                            "id": 1,
                            "name": "커뮤니티 이름",
                            "description": "커뮤니티 설명",
                            "image": "https://example.com/image.jpg",
                            "member_count": 100,
                            "favorite_count": 50,
                            "post_count": 200,
                            "score": 1000,
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="커뮤니티를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 커뮤니티가 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def get_favorite_status():
        return {
            'summary': "커뮤니티 즐겨찾기 여부 조회",
            'description': "특정 커뮤니티의 즐겨찾기 여부를 조회합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_favorite_status_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 즐겨찾기 여부 조회 성공",
                    data={"favored": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_favorite():
        return {
            'summary': "커뮤니티 즐겨찾기 추가",
            'description': "커뮤니티를 즐겨찾기에 추가합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_favorite_create_post',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 즐겨찾기 성공",
                    data={"favored": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_favorite():
        return {
            'summary': "커뮤니티 즐겨찾기 취소",
            'description': "커뮤니티 즐겨찾기를 취소합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_favorite_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 즐겨찾기 취소 성공",
                    data={"favored": False}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_favorite_list():
        return {
            'summary': "즐겨찾기 한 커뮤니티 목록 조회",
            'description': "내가 즐겨찾기 한 커뮤니티 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="즐겨찾기 한 커뮤니티 목록 조회 성공",
                    data={
                        "communities": [
                            {
                                "id": 1,
                                "name": "커뮤니티 이름",
                                "description": "커뮤니티 설명",
                                "image": "https://example.com/image.jpg",
                                "member_count": 100,
                                "favorite_count": 50,
                                "post_count": 200,
                                "score": 1000,
                                "is_active": True,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }


# Member Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class MemberSchema:
    @staticmethod
    def get_members():
        return {
            'summary': "커뮤니티 멤버 목록 조회",
            'description': "특정 커뮤니티의 멤버 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버는 제외됩니다.",
            'operation_id': 'communities_members_list_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="멤버 목록 조회 성공",
                    data={
                        "members": [
                            {
                                "id": 1,
                                "nickname": "닉네임",
                                "profile_image": "https://example.com/profile.jpg"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_member():
        return {
            'summary': "멤버 등록",
            'description': "커뮤니티에 멤버로 등록합니다. 본인만 가능하며, 이미 가입된 경우 오류가 발생합니다.",
            'request': MemberRequestSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="멤버 등록 성공",
                    data={
                        "member": {
                            "id": 1,
                            "user": 1,
                            "community": 1,
                            "nickname": "닉네임",
                            "profile_image": None,
                            "follower_count": 0,
                            "following_count": 0,
                            "post_count": 0,
                            "like_count": 0,
                            "comment_count": 0,
                            "reply_count": 0,
                            "scrap_count": 0,
                            "score": 0,
                            "is_active": True,
                            "is_staff": False,
                            "is_admin": False,
                            "is_private": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "last_access": None
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="이미 가입된 멤버입니다.",
                    errors={"detail": "이미 가입된 멤버입니다."}
                ),
                CommonExamples.error_example(
                    message="멤버 등록 실패",
                    errors={"nickname": ["이미 사용 중인 닉네임입니다."]}
                )
            ]
        }
    
    @staticmethod
    def get_member_list():
        return {
            'summary': "내가 속한 멤버 목록 조회",
            'description': "내가 속한 모든 커뮤니티의 멤버 목록을 조회합니다.",
            'operation_id': 'communities_members_my_list_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="내가 속한 멤버 목록 조회 성공",
                    data={
                        "members": [
                            {
                                "id": 1,
                                "user": 1,
                                "community": {
                                    "id": 1,
                                    "name": "커뮤니티 이름",
                                    "image": "https://example.com/image.jpg",
                                    "description": "커뮤니티 설명",
                                    "member_count": 100,
                                    "favorite_count": 50,
                                    "post_count": 200,
                                    "score": 1000
                                },
                                "nickname": "닉네임",
                                "profile_image": None,
                                "follower_count": 0,
                                "following_count": 0,
                                "post_count": 0,
                                "like_count": 0,
                                "comment_count": 0,
                                "reply_count": 0,
                                "scrap_count": 0,
                                "score": 0,
                                "is_active": True,
                                "is_staff": False,
                                "is_admin": False,
                                "is_private": False,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "last_access": None
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }
    
    @staticmethod
    def get_member_detail():
        return {
            'summary': "멤버 정보 조회",
            'description': "특정 멤버의 정보를 조회합니다. 비공개일 경우 본인 + 팔로워에게 공개, 공개일 경우 모두에게 공개됩니다.",
            'operation_id': 'communities_members_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="멤버 정보 조회 성공",
                    data={
                        "member": {
                            "id": 1,
                            "user": 1,
                            "community": 1,
                            "nickname": "닉네임",
                            "profile_image": "https://example.com/profile.jpg",
                            "follower_count": 10,
                            "following_count": 5,
                            "post_count": 20,
                            "like_count": 50,
                            "comment_count": 30,
                            "reply_count": 15,
                            "scrap_count": 5,
                            "score": 100,
                            "is_active": True,
                            "is_staff": False,
                            "is_admin": False,
                            "is_private": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "last_access": "2024-01-01T12:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "비공개 계정입니다. 팔로우 후 조회 가능합니다."}
                ),
                CommonExamples.error_example(
                    message="멤버를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 멤버가 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def update_member():
        return {
            'summary': "멤버 정보 수정",
            'description': "멤버 정보를 수정합니다. 본인만 가능합니다.",
            'request': MemberRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="멤버 정보 수정 성공",
                    data={
                        "member": {
                            "id": 1,
                            "user": 1,
                            "community": 1,
                            "nickname": "수정된 닉네임",
                            "profile_image": "https://example.com/new_profile.jpg",
                            "follower_count": 10,
                            "following_count": 5,
                            "post_count": 20,
                            "like_count": 50,
                            "comment_count": 30,
                            "reply_count": 15,
                            "scrap_count": 5,
                            "score": 100,
                            "is_active": True,
                            "is_staff": False,
                            "is_admin": False,
                            "is_private": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T12:00:00Z",
                            "last_access": "2024-01-01T12:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="멤버 정보 수정 실패",
                    errors={"nickname": ["이미 사용 중인 닉네임입니다."]}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 수정할 수 있습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_member():
        return {
            'summary': "멤버 탈퇴",
            'description': "커뮤니티에서 멤버를 탈퇴합니다. 본인만 가능합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="멤버 탈퇴 성공"
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 탈퇴할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="멤버를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 멤버가 존재하지 않습니다."}
                )
            ]
        }


# Follower Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class FollowerSchema:
    @staticmethod
    def get_followers():
        return {
            'summary': "팔로워 목록 조회",
            'description': "특정 멤버의 팔로워 목록을 조회합니다. 본인인 경우 팔로워 목록과 팔로우 요청 목록 모두 조회되며, 본인이 아닌 경우 팔로워 목록만 조회됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="팔로워 목록 조회 성공",
                    data={
                        "followers": [
                            {
                                "id": 1,
                                "follower": 2,
                                "following": 1,
                                "status": "ACCEPTED",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "next": "http://example.com/api/communities/members/1/followers?cursor=abc123",
                            "previous": None,
                            "page_size": 20
                        }
                    }
                ),
                CommonExamples.success_example(
                    message="팔로워 목록 조회 성공",
                    data={
                        "followers": [
                            {
                                "id": 1,
                                "follower": 2,
                                "following": 1,
                                "status": "ACCEPTED",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "비공개 계정입니다. 팔로우 후 조회 가능합니다."}
                )
            ]
        }
    
    @staticmethod
    def accept_follower():
        return {
            'summary': "팔로우 요청 수락",
            'description': "팔로우 요청을 수락합니다. 본인만 가능합니다.",
            'operation_id': 'communities_followers_accept',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="팔로우 요청 수락 성공",
                    data={
                        "follow": {
                            "id": 1,
                            "follower": 2,
                            "following": 1,
                            "status": "ACCEPTED",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="팔로우 요청이 없습니다.",
                    errors={"detail": "팔로우 요청이 없습니다."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 수락할 수 있습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_follower():
        return {
            'summary': "팔로워 삭제",
            'description': "팔로워를 삭제합니다. 본인만 가능합니다.",
            'operation_id': 'communities_followers_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="팔로워 삭제 성공"
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 삭제할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="팔로워를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 팔로워가 존재하지 않습니다."}
                )
            ]
        }


# Following Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class FollowingSchema:
    @staticmethod
    def get_followings():
        return {
            'summary': "팔로잉 목록 조회",
            'description': "특정 멤버의 팔로잉 목록을 조회합니다. 본인인 경우 팔로잉 목록과 팔로우 요청 모두 조회되며, 본인이 아닌 경우 팔로잉 목록만 조회됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="팔로잉 목록 조회 성공",
                    data={
                        "followings": [
                            {
                                "id": 1,
                                "follower": 1,
                                "following": 2,
                                "status": "ACCEPTED",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "next": "http://example.com/api/communities/members/1/followings?cursor=abc123",
                            "previous": None,
                            "page_size": 20
                        }
                    }
                ),
                CommonExamples.success_example(
                    message="팔로잉 목록 조회 성공",
                    data={
                        "followings": [
                            {
                                "id": 1,
                                "follower": 1,
                                "following": 2,
                                "status": "ACCEPTED",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "비공개 계정입니다. 팔로우 후 조회 가능합니다."}
                )
            ]
        }
    
    @staticmethod
    def create_following():
        return {
            'summary': "팔로우 요청",
            'description': "다른 멤버를 팔로우하거나 팔로우 요청을 보냅니다. 본인만 가능하며, 비공개 계정인 경우 요청 상태로 생성되고, 공개 계정인 경우 즉시 팔로우됩니다.",
            'operation_id': 'communities_followings_create',
            'request': None,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="팔로우 요청 성공",
                    data={
                        "follow": {
                            "id": 1,
                            "follower": 1,
                            "following": 2,
                            "status": "PENDING",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.success_example(
                    message="팔로우 성공",
                    data={}
                ),
                CommonExamples.error_example(
                    message="자기 자신을 팔로우할 수 없습니다.",
                    errors={"detail": "자기 자신을 팔로우할 수 없습니다."}
                ),
                CommonExamples.error_example(
                    message="이미 팔로우 요청이 존재합니다.",
                    errors={"detail": "이미 팔로우 요청이 존재합니다."}
                ),
                CommonExamples.error_example(
                    message="내가 차단한 사용자입니다.",
                    errors={"detail": "내가 차단한 사용자입니다."}
                ),
                CommonExamples.error_example(
                    message="이 사용자에게 차단되었습니다.",
                    errors={"detail": "이 사용자에게 차단되었습니다."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 팔로우할 수 있습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_following():
        return {
            'summary': "팔로우 취소",
            'description': "팔로우를 취소하거나 팔로우 요청을 취소합니다. 본인만 가능합니다.",
            'operation_id': 'communities_followings_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="팔로우 취소 성공"
                ),
                CommonExamples.success_example(
                    message="팔로우 요청 취소 성공"
                ),
                CommonExamples.error_example(
                    message="팔로우되지 않았습니다.",
                    errors={"detail": "팔로우되지 않았습니다."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 취소할 수 있습니다."}
                )
            ]
        }


# Block Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class BlockSchema:
    @staticmethod
    def get_blocks():
        return {
            'summary': "차단 목록 조회",
            'description': "차단한 멤버 목록을 조회합니다. 본인만 가능합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="차단 목록 조회 성공",
                    data={
                        "blocks": [
                            {
                                "id": 1,
                                "follower": 1,
                                "following": 2,
                                "status": "BLOCKED",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 조회할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="멤버를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 멤버가 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def create_block():
        return {
            'summary': "차단 추가",
            'description': "멤버를 차단합니다. 본인만 가능하며, 차단 시 양방향 팔로우 관계가 해제됩니다.",
            'operation_id': 'communities_blocks_create',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="차단 성공",
                    data={
                        "block": {
                            "id": 1,
                            "follower": 1,
                            "following": 2,
                            "status": "BLOCKED",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="자기 자신을 차단할 수 없습니다.",
                    errors={"detail": "자기 자신을 차단할 수 없습니다."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 차단할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="멤버를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 멤버가 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_block():
        return {
            'summary': "차단 해제",
            'description': "차단을 해제합니다. 본인만 가능합니다.",
            'operation_id': 'communities_blocks_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="차단 해제 성공"
                ),
                CommonExamples.error_example(
                    message="차단되지 않았습니다.",
                    errors={"detail": "차단되지 않았습니다."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "본인만 해제할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="멤버를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 멤버가 존재하지 않습니다."}
                )
            ]
        }


# Post Category Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class PostCategorySchema:
    @staticmethod
    def get_categories():
        return {
            'summary': "카테고리 목록 조회",
            'description': "커뮤니티의 카테고리 목록을 조회합니다. 멤버만 가능합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="카테고리 목록 조회 성공",
                    data={
                        "categories": [
                            {
                                "id": 1,
                                "parent": None,
                                "name": "카테고리 이름",
                                "description": "카테고리 설명",
                                "image": "https://example.com/image.jpg",
                                "favorite_count": 10,
                                "post_count": 50,
                                "score": 100,
                                "created_at": "2024-01-01T00:00:00Z"
                            },
                            {
                                "id": 2,
                                "parent": {
                                    "id": 1,
                                    "name": "부모 카테고리",
                                    "image": "https://example.com/parent.jpg",
                                    "description": "부모 카테고리 설명",
                                    "favorite_count": 5,
                                    "post_count": 20,
                                    "score": 50
                                },
                                "name": "하위 카테고리",
                                "description": "하위 카테고리 설명",
                                "image": None,
                                "favorite_count": 3,
                                "post_count": 10,
                                "score": 30,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_category_detail():
        return {
            'summary': "카테고리 상세 조회",
            'description': "특정 카테고리의 상세 정보를 조회합니다. 멤버만 가능합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="카테고리 상세 조회 성공",
                    data={
                        "category": {
                            "id": 1,
                            "parent": None,
                            "name": "카테고리 이름",
                            "description": "카테고리 설명",
                            "image": "https://example.com/image.jpg",
                            "favorite_count": 10,
                            "post_count": 50,
                            "score": 100,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                ),
                CommonExamples.error_example(
                    message="카테고리를 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 카테고리가 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def get_favorite_status():
        return {
            'summary': "카테고리 즐겨찾기 여부 조회",
            'description': "특정 카테고리의 즐겨찾기 여부를 조회합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_categories_favorites_status_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="카테고리 즐겨찾기 여부 조회 성공",
                    data={"favored": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_favorite():
        return {
            'summary': "카테고리 즐겨찾기 추가",
            'description': "카테고리를 즐겨찾기에 추가합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_categories_favorites_create',
            'request': None,
            'responses': {
                201: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="카테고리 즐겨찾기 성공",
                    data={"favored": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_favorite():
        return {
            'summary': "카테고리 즐겨찾기 취소",
            'description': "카테고리 즐겨찾기를 취소합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_categories_favorites_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="카테고리 즐겨찾기 취소 성공",
                    data={"favored": False}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }


# Post Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class PostSchema:
    @staticmethod
    def get_posts():
        return {
            'summary': "카테고리 내 글 목록 조회",
            'description': "특정 카테고리의 글 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버의 글은 제외됩니다. 부모 카테고리인 경우 하위 카테고리의 글도 포함됩니다.",
            'operation_id': 'communities_posts_list_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="카테고리 내 글 목록 조회 성공",
                    data={
                        "posts": [
                            {
                                "id": 1,
                                "title": "글 제목",
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 10,
                                "comment_count": 5,
                                "scrap_count": 3,
                                "score": 100,
                                "is_liked": False,
                                "is_scraped": False,
                                "is_following": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 5,
                            "total_count": 100
                        }
                    }
                ),
                CommonExamples.success_example(
                    message="카테고리 내 글 목록 조회 성공",
                    data={
                        "posts": [
                            {
                                "id": 1,
                                "title": "글 제목",
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 10,
                                "comment_count": 5,
                                "scrap_count": 3,
                                "score": 100,
                                "is_liked": False,
                                "is_scraped": False,
                                "is_following": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_post():
        return {
            'summary': "글 작성",
            'description': "새로운 글을 작성합니다. 멤버만 가능합니다.",
            'request': PostRequestSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="글 작성 성공",
                    data={
                        "post": {
                            "title": "글 제목",
                            "content": "글 내용",
                            "images": ["https://example.com/image1.jpg"],
                            "is_anonymous": False
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="글 작성 실패",
                    errors={
                        "title": ["이 필드는 필수입니다."],
                        "content": ["이 필드는 필수입니다."]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_posts_by_community():
        return {
            'summary': "커뮤니티 내 글 목록 조회",
            'description': "특정 커뮤니티의 모든 글 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버의 글은 제외됩니다.",
            'operation_id': 'communities_posts_by_community_list_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 내 글 목록 조회 성공",
                    data={
                        "posts": [
                            {
                                "id": 1,
                                "title": "글 제목",
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 10,
                                "comment_count": 5,
                                "scrap_count": 3,
                                "score": 100,
                                "is_liked": False,
                                "is_scraped": False,
                                "is_following": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 5,
                            "total_count": 100
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_posts_by_member():
        return {
            'summary': "내가 속한 커뮤니티 글 목록 조회",
            'description': "내가 속한 모든 커뮤니티의 글 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버의 글은 제외됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 내 글 목록 조회 성공",
                    data={
                        "posts": [
                            {
                                "id": 1,
                                "title": "글 제목",
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 10,
                                "comment_count": 5,
                                "scrap_count": 3,
                                "score": 100,
                                "is_liked": False,
                                "is_scraped": False,
                                "is_following": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 5,
                            "total_count": 100
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }
    
    @staticmethod
    def get_posts_by_favorite_community():
        return {
            'summary': "즐겨찾는 커뮤니티의 글 목록 조회",
            'description': "내가 즐겨찾기 한 커뮤니티의 글 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버의 글은 제외됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 내 글 목록 조회 성공",
                    data={
                        "posts": [
                            {
                                "id": 1,
                                "title": "글 제목",
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 10,
                                "comment_count": 5,
                                "scrap_count": 3,
                                "score": 100,
                                "is_liked": False,
                                "is_scraped": False,
                                "is_following": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 5,
                            "total_count": 100
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }
    
    @staticmethod
    def get_posts_by_favorite_category():
        return {
            'summary': "즐겨찾는 카테고리의 글 목록 조회",
            'description': "커뮤니티 내에서 내가 즐겨찾기 한 카테고리의 글 목록을 조회합니다. 본인만 가능하며, 차단된 멤버의 글은 제외됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="커뮤니티 내 글 목록 조회 성공",
                    data={
                        "posts": [
                            {
                                "id": 1,
                                "title": "글 제목",
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 10,
                                "comment_count": 5,
                                "scrap_count": 3,
                                "score": 100,
                                "is_liked": False,
                                "is_scraped": False,
                                "is_following": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 5,
                            "total_count": 100
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_post_detail():
        return {
            'summary': "글 상세 조회",
            'description': "특정 글의 상세 정보를 조회합니다. 멤버만 가능하며, 차단된 멤버의 글은 조회할 수 없습니다.",
            'operation_id': 'communities_posts_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 상세 조회 성공",
                    data={
                        "post": {
                            "id": 1,
                            "title": "글 제목",
                            "content": "글 내용",
                            "images": ["https://example.com/image1.jpg"],
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 10,
                            "comment_count": 5,
                            "reply_count": 3,
                            "scrap_count": 3,
                            "score": 100,
                            "is_liked": False,
                            "is_scraped": False,
                            "is_following": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T12:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post 상세 조회 실패",
                    errors={"detail": "차단된 멤버입니다."}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                ),
                CommonExamples.error_example(
                    message="글을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 글이 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def update_post():
        return {
            'summary': "글 수정",
            'description': "글을 수정합니다. 멤버이면서 작성자만 가능합니다.",
            'request': PostRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 수정 성공",
                    data={
                        "post": {
                            "title": "수정된 글 제목",
                            "content": "수정된 글 내용",
                            "images": ["https://example.com/new_image.jpg"],
                            "is_anonymous": False
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post 수정 실패",
                    errors={
                        "title": ["이 필드는 필수입니다."]
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "작성자만 수정할 수 있습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_post():
        return {
            'summary': "글 삭제",
            'description': "글을 삭제합니다. 멤버이면서 작성자만 가능합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 삭제 성공"
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "작성자만 삭제할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="글을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 글이 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def get_like_status():
        return {
            'summary': "글 좋아요 여부 조회",
            'description': "특정 글의 좋아요 여부를 조회합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_posts_likes_status_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 좋아요 여부 조회 성공",
                    data={"liked": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_like():
        return {
            'summary': "글 좋아요",
            'description': "글에 좋아요를 추가합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_posts_likes_create',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 좋아요 성공",
                    data={"liked": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_like():
        return {
            'summary': "글 좋아요 취소",
            'description': "글의 좋아요를 취소합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_posts_likes_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 좋아요 취소 성공",
                    data={"liked": False}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_scrap_status():
        return {
            'summary': "글 스크랩 여부 조회",
            'description': "특정 글의 스크랩 여부를 조회합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_posts_scraps_status_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 스크랩 여부 조회 성공",
                    data={"scraped": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_scrap():
        return {
            'summary': "글 스크랩",
            'description': "글을 스크랩합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_posts_scraps_create',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 스크랩 성공",
                    data={"scraped": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_scrap():
        return {
            'summary': "글 스크랩 취소",
            'description': "글의 스크랩을 취소합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_posts_scraps_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post 스크랩 취소 성공",
                    data={"scraped": False}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }


# Post Comment Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class PostCommentSchema:
    @staticmethod
    def get_comments():
        return {
            'summary': "댓글 목록 조회",
            'description': "특정 글의 댓글 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버의 댓글은 제외됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 목록 조회 성공",
                    data={
                        "comments": [
                            {
                                "id": 1,
                                "content": "댓글 내용",
                                "image": None,
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 5,
                                "reply_count": 2,
                                "score": 50,
                                "is_liked": False,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 3,
                            "total_count": 50
                        }
                    }
                ),
                CommonExamples.success_example(
                    message="Post Comment 목록 조회 성공",
                    data={
                        "comments": [
                            {
                                "id": 1,
                                "content": "댓글 내용",
                                "image": None,
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 5,
                                "reply_count": 2,
                                "score": 50,
                                "is_liked": False,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_comment():
        return {
            'summary': "댓글 작성",
            'description': "글에 댓글을 작성합니다. 멤버만 가능합니다.",
            'request': PostCommentRequestSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 작성 성공",
                    data={
                        "comment": {
                            "id": 1,
                            "content": "댓글 내용",
                            "image": None,
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 0,
                            "reply_count": 0,
                            "score": 0,
                            "is_liked": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post Comment 작성 실패",
                    errors={
                        "content": ["이 필드는 필수입니다."]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_comment_detail():
        return {
            'summary': "댓글 상세 조회",
            'description': "특정 댓글의 상세 정보를 조회합니다. 멤버만 가능하며, 차단된 멤버의 댓글은 조회할 수 없습니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 상세 조회 성공",
                    data={
                        "comment": {
                            "id": 1,
                            "content": "댓글 내용",
                            "image": None,
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 5,
                            "reply_count": 2,
                            "score": 50,
                            "is_liked": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post Comment 상세 조회 실패",
                    errors={"detail": "차단된 멤버입니다."}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                ),
                CommonExamples.error_example(
                    message="댓글을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 댓글이 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def update_comment():
        return {
            'summary': "댓글 수정",
            'description': "댓글을 수정합니다. 멤버이면서 작성자만 가능합니다.",
            'request': PostCommentRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 수정 성공",
                    data={
                        "comment": {
                            "id": 1,
                            "content": "수정된 댓글 내용",
                            "image": "https://example.com/image.jpg",
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 5,
                            "reply_count": 2,
                            "score": 50,
                            "is_liked": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T12:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post Comment 수정 실패",
                    errors={
                        "content": ["이 필드는 필수입니다."]
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "작성자만 수정할 수 있습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_comment():
        return {
            'summary': "댓글 삭제",
            'description': "댓글을 삭제합니다. 멤버이면서 작성자만 가능합니다. 대댓글이 있으면 소프트 삭제되고, 없으면 실제 삭제됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 삭제 성공"
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "작성자만 삭제할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="댓글을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 댓글이 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def get_like_status():
        return {
            'summary': "댓글 좋아요 여부 조회",
            'description': "특정 댓글의 좋아요 여부를 조회합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_post_comments_likes_status_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 좋아요 여부 조회 성공",
                    data={"liked": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_like():
        return {
            'summary': "댓글 좋아요",
            'description': "댓글에 좋아요를 추가합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_post_comments_likes_create',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 좋아요 성공",
                    data={"liked": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_like():
        return {
            'summary': "댓글 좋아요 취소",
            'description': "댓글의 좋아요를 취소합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_post_comments_likes_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Comment 좋아요 취소 성공",
                    data={"liked": False}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }


# Post Reply Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class PostReplySchema:
    @staticmethod
    def get_replies():
        return {
            'summary': "대댓글 목록 조회",
            'description': "특정 댓글의 대댓글 목록을 조회합니다. 멤버만 가능하며, 차단된 멤버의 대댓글은 제외됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 목록 조회 성공",
                    data={
                        "replies": [
                            {
                                "id": 1,
                                "content": "대댓글 내용",
                                "image": None,
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 3,
                                "score": 30,
                                "is_liked": False,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_pages": 2,
                            "total_count": 30
                        }
                    }
                ),
                CommonExamples.success_example(
                    message="Post Reply 목록 조회 성공",
                    data={
                        "replies": [
                            {
                                "id": 1,
                                "content": "대댓글 내용",
                                "image": None,
                                "author": {
                                    "id": 1,
                                    "nickname": "작성자",
                                    "profile_image": "https://example.com/profile.jpg"
                                },
                                "like_count": 3,
                                "score": 30,
                                "is_liked": False,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_reply():
        return {
            'summary': "대댓글 작성",
            'description': "댓글에 대댓글을 작성합니다. 멤버만 가능합니다.",
            'request': PostReplyRequestSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 작성 성공",
                    data={
                        "reply": {
                            "id": 1,
                            "content": "대댓글 내용",
                            "image": None,
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 0,
                            "score": 0,
                            "is_liked": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post Reply 작성 실패",
                    errors={
                        "content": ["이 필드는 필수입니다."]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def get_reply_detail():
        return {
            'summary': "대댓글 상세 조회",
            'description': "특정 대댓글의 상세 정보를 조회합니다. 멤버만 가능하며, 차단된 멤버의 대댓글은 조회할 수 없습니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 상세 조회 성공",
                    data={
                        "reply": {
                            "id": 1,
                            "content": "대댓글 내용",
                            "image": None,
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 3,
                            "score": 30,
                            "is_liked": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post Reply 상세 조회 실패",
                    errors={"detail": "차단된 멤버입니다."}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                ),
                CommonExamples.error_example(
                    message="대댓글을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 대댓글이 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def update_reply():
        return {
            'summary': "대댓글 수정",
            'description': "대댓글을 수정합니다. 멤버이면서 작성자만 가능합니다.",
            'request': PostReplyRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 수정 성공",
                    data={
                        "reply": {
                            "id": 1,
                            "content": "수정된 대댓글 내용",
                            "image": "https://example.com/image.jpg",
                            "author": {
                                "id": 1,
                                "nickname": "작성자",
                                "profile_image": "https://example.com/profile.jpg"
                            },
                            "like_count": 3,
                            "score": 30,
                            "is_liked": False,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T12:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="Post Reply 수정 실패",
                    errors={
                        "content": ["이 필드는 필수입니다."]
                    }
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "작성자만 수정할 수 있습니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_reply():
        return {
            'summary': "대댓글 삭제",
            'description': "대댓글을 삭제합니다. 멤버이면서 작성자만 가능합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 삭제 성공"
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "작성자만 삭제할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="대댓글을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 대댓글이 존재하지 않습니다."}
                )
            ]
        }
    
    @staticmethod
    def get_like_status():
        return {
            'summary': "대댓글 좋아요 여부 조회",
            'description': "특정 대댓글의 좋아요 여부를 조회합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_post_replies_likes_status_get',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 좋아요 여부 조회 성공",
                    data={"liked": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def create_like():
        return {
            'summary': "대댓글 좋아요",
            'description': "대댓글에 좋아요를 추가합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_post_replies_likes_create',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 좋아요 성공",
                    data={"liked": True}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
    
    @staticmethod
    def delete_like():
        return {
            'summary': "대댓글 좋아요 취소",
            'description': "대댓글의 좋아요를 취소합니다. 멤버이면서 본인만 가능합니다.",
            'operation_id': 'communities_post_replies_likes_delete',
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="Post Reply 좋아요 취소 성공",
                    data={"liked": False}
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "해당 커뮤니티의 멤버가 아닙니다."}
                )
            ]
        }
