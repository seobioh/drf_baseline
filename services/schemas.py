# services/schemas.py
app_name = "services"

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


# Services Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class ServicesSchema:
    @staticmethod
    def get_notices():
        return {
            'summary': "공지사항 목록 조회",
            'description': "활성화된 공지사항 목록을 조회합니다. 서비스별 필터링이 가능합니다.",
            'operation_id': 'services_notices_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="공지사항 조회 성공",
                    data={
                        "notices": [
                            {
                                "id": 1,
                                "service": "main",
                                "title": "시스템 점검 안내",
                                "subtitle": "2024년 1월 15일 시스템 점검 예정",
                                "description": "시스템 안정성 향상을 위한 점검을 실시합니다.",
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
    def get_notice_detail():
        return {
            'summary': "공지사항 상세 조회",
            'description': "특정 공지사항의 상세 정보를 조회합니다.",
            'operation_id': 'services_notices_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="공지사항 조회 성공",
                    data={
                        "notice": {
                            "id": 1,
                            "service": "main",
                            "title": "시스템 점검 안내",
                            "subtitle": "2024년 1월 15일 시스템 점검 예정",
                            "description": "시스템 안정성 향상을 위한 점검을 실시합니다.",
                            "mobile_img": "https://example.com/mobile.jpg",
                            "desktop_img": "https://example.com/desktop.jpg",
                            "detail_img": "https://example.com/detail.jpg",
                            "link": "https://example.com/notice/1",
                            "start_date": "2024-01-01T00:00:00Z",
                            "end_date": "2024-01-31T23:59:59Z",
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="공지사항을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 공지사항이 존재하지 않습니다."}
                )
            ]
        }

    @staticmethod
    def get_events():
        return {
            'summary': "이벤트 목록 조회",
            'description': "활성화된 이벤트 목록을 조회합니다. 서비스별 필터링이 가능합니다.",
            'operation_id': 'services_events_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="이벤트 조회 성공",
                    data={
                        "events": [
                            {
                                "id": 1,
                                "service": "main",
                                "title": "신규 사용자 이벤트",
                                "subtitle": "첫 가입 시 포인트 지급",
                                "description": "신규 가입 시 1000포인트를 지급합니다.",
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
    def get_event_detail():
        return {
            'summary': "이벤트 상세 조회",
            'description': "특정 이벤트의 상세 정보를 조회합니다.",
            'operation_id': 'services_events_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="이벤트 조회 성공",
                    data={
                        "event": {
                            "id": 1,
                            "service": "main",
                            "title": "신규 사용자 이벤트",
                            "subtitle": "첫 가입 시 포인트 지급",
                            "description": "신규 가입 시 1000포인트를 지급합니다.",
                            "mobile_img": "https://example.com/mobile.jpg",
                            "desktop_img": "https://example.com/desktop.jpg",
                            "detail_img": "https://example.com/detail.jpg",
                            "link": "https://example.com/event/1",
                            "start_date": "2024-01-01T00:00:00Z",
                            "end_date": "2024-01-31T23:59:59Z",
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                )
            ]
        }

    @staticmethod
    def get_ads():
        return {
            'summary': "광고 목록 조회",
            'description': "활성화된 광고 목록을 조회합니다. 서비스별 필터링이 가능합니다.",
            'operation_id': 'services_ads_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="광고 조회 성공",
                    data={
                        "ads": [
                            {
                                "id": 1,
                                "service": "main",
                                "title": "신제품 출시 광고",
                                "subtitle": "새로운 제품을 만나보세요",
                                "description": "혁신적인 기능을 갖춘 신제품을 소개합니다.",
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
    def get_ad_detail():
        return {
            'summary': "광고 상세 조회",
            'description': "특정 광고의 상세 정보를 조회합니다.",
            'operation_id': 'services_ads_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="광고 조회 성공",
                    data={
                        "ad": {
                            "id": 1,
                            "service": "main",
                            "title": "신제품 출시 광고",
                            "subtitle": "새로운 제품을 만나보세요",
                            "description": "혁신적인 기능을 갖춘 신제품을 소개합니다.",
                            "mobile_img": "https://example.com/mobile.jpg",
                            "desktop_img": "https://example.com/desktop.jpg",
                            "detail_img": "https://example.com/detail.jpg",
                            "background_img": "https://example.com/background.jpg",
                            "link": "https://example.com/ad/1",
                            "start_date": "2024-01-01T00:00:00Z",
                            "end_date": "2024-01-31T23:59:59Z",
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                )
            ]
        }

    @staticmethod
    def get_faqs():
        return {
            'summary': "FAQ 목록 조회",
            'description': "활성화된 FAQ 목록을 조회합니다. 서비스별 필터링이 가능합니다.",
            'operation_id': 'services_faqs_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="FAQ 조회 성공",
                    data={
                        "faqs": [
                            {
                                "id": 1,
                                "service": "main",
                                "question": "회원가입은 어떻게 하나요?",
                                "answer": "이메일과 비밀번호를 입력하여 회원가입할 수 있습니다.",
                                "order": 1,
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
    def get_faq_detail():
        return {
            'summary': "FAQ 상세 조회",
            'description': "특정 FAQ의 상세 정보를 조회합니다.",
            'operation_id': 'services_faqs_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="FAQ 조회 성공",
                    data={
                        "faq": {
                            "id": 1,
                            "service": "main",
                            "question": "회원가입은 어떻게 하나요?",
                            "answer": "이메일과 비밀번호를 입력하여 회원가입할 수 있습니다.",
                            "order": 1,
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                )
            ]
        }


    @staticmethod
    def get_privacy_policies():
        return {
            'summary': "개인정보처리방침 목록 조회",
            'description': "활성화된 개인정보처리방침 목록을 조회합니다. 서비스별 필터링이 가능합니다.",
            'operation_id': 'services_privacy_policies_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="개인정보처리방침 조회 성공",
                    data={
                        "privacy_policies": [
                            {
                                "id": 1,
                                "service": "main",
                                "title": "개인정보처리방침",
                                "content": "개인정보 수집 및 이용에 대한 방침입니다.",
                                "order": 1,
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
    def get_privacy_policy_detail():
        return {
            'summary': "개인정보처리방침 상세 조회",
            'description': "특정 개인정보처리방침의 상세 정보를 조회합니다.",
            'operation_id': 'services_privacy_policies_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="개인정보처리방침 조회 성공",
                    data={
                        "privacy_policy": {
                            "id": 1,
                            "service": "main",
                            "title": "개인정보처리방침",
                            "content": "개인정보 수집 및 이용에 대한 방침입니다.",
                            "order": 1,
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                )
            ]
        }

    @staticmethod
    def get_terms():
        return {
            'summary': "이용약관 목록 조회",
            'description': "활성화된 이용약관 목록을 조회합니다. 서비스별 필터링이 가능합니다.",
            'operation_id': 'services_terms_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="이용약관 조회 성공",
                    data={
                        "terms": [
                            {
                                "id": 1,
                                "service": "main",
                                "title": "서비스 이용약관",
                                "content": "서비스 이용에 대한 약관입니다.",
                                "order": 1,
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
    def get_term_detail():
        return {
            'summary': "이용약관 상세 조회",
            'description': "특정 이용약관의 상세 정보를 조회합니다.",
            'operation_id': 'services_terms_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="이용약관 조회 성공",
                    data={
                        "term": {
                            "id": 1,
                            "service": "main",
                            "title": "서비스 이용약관",
                            "content": "서비스 이용에 대한 약관입니다.",
                            "order": 1,
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                )
            ]
        }