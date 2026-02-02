# communities/schemas.py
app_name = "communities"

from drf_spectacular.utils import OpenApiExample

from server.schemas import SuccessResponseSerializer, ErrorResponseSerializer

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
            'request': None,
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
            'request': None,
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
