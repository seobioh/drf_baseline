# users/schemas.py
app_name = "users"

from drf_spectacular.utils import OpenApiExample

from server.schemas import SuccessResponseSerializer, ErrorResponseSerializer

# Common Examples
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommonExamples:
    @staticmethod
    def success_example(message="요청이 성공적으로 처리되었습니다.", data=None):
        """일반 성공 응답 예시"""
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
        """일반 오류 응답 예시"""
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


# User Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class UserSchema:
    @staticmethod
    def get_referrals():
        return {
            'summary': "추천 목록 조회",
            'description': "사용자의 추천 목록을 조회합니다. 내가 추천한 사람과 나를 추천한 사람의 목록을 반환합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="추천인 조회 성공",
                    data={
                        "referrals": {
                            "referrals_given": [
                                {
                                    "id": 1,
                                    "referrer": 1,
                                    "referrer_username": "referrer_username",
                                    "referree": 2,
                                    "referree_username": "referree_username",
                                    "created_at": "2024-01-01T00:00:00Z"
                                }
                            ],
                            "referrals_received": [
                                {
                                    "id": 2,
                                    "referrer": 3,
                                    "referrer_username": "referrer_username",
                                    "referree": 1,
                                    "referree_username": "referree_username",
                                    "created_at": "2024-01-01T00:00:00Z"
                                }
                            ]
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
    def create_referral():
        return {
            'summary': "추천 생성",
            'description': "추천 코드를 사용하여 추천을 생성합니다. 한 사용자는 한 번만 추천할 수 있습니다.",
            'request': None,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="추천인 등록 성공",
                    data={
                        "referral": {
                            "id": 1,
                            "referrer": 1,
                            "referrer_username": "referrer_username",
                            "referree": 2,
                            "referree_username": "referree_username",
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="자기 자신을 추천할 수 없습니다.",
                    errors={"detail": "자기 자신을 추천할 수 없습니다."}
                ),
                CommonExamples.error_example(
                    message="한 명만 추천할 수 있습니다.",
                    errors={"detail": "한 번만 추천할 수 있습니다."}
                ),
                CommonExamples.error_example(
                    message="Not found",
                    errors={"detail": "유효하지 않은 추천 코드입니다."}
                )
            ]
        }

    @staticmethod
    def use_coupon():
        return {
            'summary': "포인트 쿠폰 사용",
            'description': "포인트 쿠폰을 사용하여 포인트를 획득합니다.",
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="쿠폰 사용 성공",
                    data={}
                ),
                CommonExamples.error_example(
                    message="쿠폰을 사용할 수 없습니다.",
                    errors={"detail": "쿠폰 사용 한도를 초과했습니다."}
                ),
                CommonExamples.error_example(
                    message="쿠폰 사용 한도를 초과했습니다.",
                    errors={"detail": "개인 사용 한도를 초과했습니다."}
                ),
                CommonExamples.error_example(
                    message="유효하지 않은 쿠폰입니다.",
                    errors={"detail": "유효하지 않은 쿠폰입니다."}
                ),
                CommonExamples.error_example(
                    message="Not found",
                    errors={"detail": "존재하지 않는 쿠폰입니다."}
                )
            ]
        }

    @staticmethod
    def get_point_transactions():
        return {
            'summary': "포인트 거래 내역 조회",
            'description': "사용자의 포인트 거래 내역을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="포인트 내역 조회 성공",
                    data={
                        "point_transactions": [
                            {
                                "id": 1,
                                "user": 1,
                                "transaction_id": 1,
                                "amount": 1000,
                                "transaction_type": "COUPON",
                                "description": "쿠폰 사용",
                                "created_at": "2024-01-01T00:00:00Z"
                            },
                            {
                                "id": 2,
                                "user": 1,
                                "transaction_id": 2,
                                "amount": 500,
                                "transaction_type": "REFERRAL",
                                "description": "추천 등록",
                                "created_at": "2024-01-01T00:00:00Z"
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