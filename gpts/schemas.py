# gpts/schemas.py
app_name = "gpts"

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


# GPT Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class GPTSchema:
    @staticmethod
    def get_gpt_prompts():
        return {
            'summary': "GPT 프롬프트 목록 조회",
            'description': "활성화된 GPT 프롬프트 목록을 조회합니다.",
            'operation_id': 'gpts_prompts_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="GPT 프롬프트 조회 성공",
                    data={
                        "gpt_prompts": [
                            {
                                "id": 1,
                                "name": "일반 대화",
                                "description": "일상적인 대화를 위한 프롬프트",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                )
            ]
        }

    @staticmethod
    def get_gpt_chat_rooms():
        return {
            'summary': "GPT 채팅방 목록 조회",
            'description': "현재 사용자의 활성 채팅방 목록을 조회합니다.",
            'operation_id': 'gpts_chat_rooms_list_get',
            'responses': {
                200: SuccessResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="GPT 채팅방 조회 성공",
                    data={
                        "gpt_chat_rooms": [
                            {
                                "id": 1,
                                "name": "새 채팅방",
                                "user": 1,
                                "prompt": 1,
                                "summary": None,
                                "summary_token_count": 0,
                                "last_summarized_message": None,
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z"
                            }
                        ]
                    }
                )
            ]
        }

    @staticmethod
    def create_gpt_chat_room():
        return {
            'summary': "GPT 채팅방 생성",
            'description': "새 GPT 채팅방을 생성합니다.",
            'operation_id': 'gpts_chat_room_create_post',
            'request': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'maxLength': 100,
                        'description': '채팅방 이름',
                        'example': '새 채팅방',
                    },
                    'prompt': {
                        'type': 'integer',
                        'nullable': True,
                        'description': 'GPT 프롬프트 ID (선택)',
                    },
                },
                'required': [],
            },
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                OpenApiExample(
                    "Request Example",
                    summary="요청 예시",
                    description="채팅방 생성 요청",
                    value={"name": "새 채팅방", "prompt": 1},
                    request_only=True
                ),
                CommonExamples.success_example(
                    message="GPT 채팅방 생성 성공",
                    data={
                        "gpt_chat_room": {
                            "id": 1,
                            "name": "새 채팅방",
                            "user": 1,
                            "prompt": 1,
                            "summary": None,
                            "summary_token_count": 0,
                            "last_summarized_message": None,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="GPT 채팅방 생성 실패",
                    errors={"name": ["이 필드는 blank일 수 없습니다."]}
                )
            ]
        }

    @staticmethod
    def get_gpt_chat_room_detail():
        return {
            'summary': "GPT 채팅방 상세 조회",
            'description': "특정 GPT 채팅방의 상세 정보를 조회합니다.",
            'operation_id': 'gpts_chat_room_detail_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="GPT 채팅방 상세 조회 성공",
                    data={
                        "gpt_chat_room": {
                            "id": 1,
                            "name": "새 채팅방",
                            "user": 1,
                            "prompt": 1,
                            "summary": None,
                            "summary_token_count": 0,
                            "last_summarized_message": None,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="GPT 채팅방을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 채팅방이 존재하지 않거나 접근 권한이 없습니다."}
                )
            ]
        }

    @staticmethod
    def update_gpt_chat_room():
        return {
            'summary': "GPT 채팅방 수정",
            'description': "GPT 채팅방 정보를 수정합니다.",
            'operation_id': 'gpts_chat_room_update_put',
            'request': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'maxLength': 100,
                        'description': '채팅방 이름',
                    },
                    'prompt': {
                        'type': 'integer',
                        'nullable': True,
                        'description': 'GPT 프롬프트 ID (선택)',
                    },
                },
                'required': [],
            },
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                OpenApiExample(
                    "Request Example",
                    summary="요청 예시",
                    description="채팅방 수정 요청",
                    value={"name": "수정된 채팅방"},
                    request_only=True
                ),
                CommonExamples.success_example(
                    message="GPT 채팅방 수정 성공",
                    data={
                        "gpt_chat_room": {
                            "id": 1,
                            "name": "수정된 채팅방",
                            "user": 1,
                            "prompt": 1,
                            "summary": None,
                            "summary_token_count": 0,
                            "last_summarized_message": None,
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="GPT 채팅방 수정 실패",
                    errors={"name": ["이 필드는 blank일 수 없습니다."]}
                )
            ]
        }

    @staticmethod
    def delete_gpt_chat_room():
        return {
            'summary': "GPT 채팅방 삭제",
            'description': "GPT 채팅방을 삭제합니다.",
            'operation_id': 'gpts_chat_room_delete',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="GPT 채팅방 삭제 성공",
                ),
                CommonExamples.error_example(
                    message="GPT 채팅방을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 채팅방이 존재하지 않거나 접근 권한이 없습니다."}
                )
            ]
        }

    @staticmethod
    def get_gpt_chat_message_detail():
        return {
            'summary': "GPT 채팅 메시지 목록 조회",
            'description': "특정 채팅방의 메시지 목록을 페이지네이션으로 조회합니다. query: page, page_size(선택, 기본 20, 최대 100).",
            'operation_id': 'gpts_chat_messages_list_get',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="GPT 채팅메시지 조회 성공",
                    data={
                        "gpt_chat_messages": [
                            {
                                "id": 1,
                                "chat_room": 1,
                                "role": "user",
                                "model": "gpt-4o-mini",
                                "message": "안녕하세요",
                                "token_count": 10,
                                "is_error": False,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "count": 1,
                        "next": None,
                        "previous": None,
                    }
                ),
                CommonExamples.error_example(
                    message="GPT 채팅방을 찾을 수 없습니다.",
                    errors={"detail": "해당 ID의 채팅방이 존재하지 않거나 접근 권한이 없습니다."}
                )
            ]
        }

    @staticmethod
    def create_gpt_chat_message():
        return {
            'summary': "GPT 채팅 메시지 전송",
            'description': "채팅방에 사용자 메시지를 전송하고, GPT 스트리밍 응답을 받습니다.",
            'operation_id': 'gpts_chat_message_create_post',
            'request': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': '전송할 메시지 내용',
                        'example': '안녕하세요',
                    },
                    'model': {
                        'type': 'string',
                        'enum': ['gpt-4o-mini', 'gpt-4o', 'gpt-4o-turbo'],
                        'description': '사용할 GPT 모델',
                        'default': 'gpt-4o-mini',
                    },
                },
                'required': ['message'],
            },
            'responses': {
                200: {
                    'description': 'text/event-stream 스트리밍 응답',
                    'content': {
                        'text/event-stream': {
                            'schema': {
                                'type': 'string',
                                'description': 'GPT 응답 스트림 (SSE)',
                            }
                        }
                    }
                },
                400: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                OpenApiExample(
                    "Request Example",
                    summary="요청 예시",
                    description="메시지 전송 요청",
                    value={"message": "안녕하세요", "model": "gpt-4o-mini"},
                    request_only=True
                ),
                CommonExamples.error_example(
                    message="GPT 채팅메시지 생성 실패",
                    errors={"message": ["이 필드는 blank일 수 없습니다."]}
                )
            ]
        }

    @staticmethod
    def start_gpt():
        return {
            'summary': "GPT 채팅 시작 (방 생성 + 첫 메시지 스트리밍)",
            'description': "프롬프트와 첫 메시지로 채팅방을 생성하고, GPT 스트리밍 응답을 바로 받습니다.",
            'operation_id': 'gpts_start_post',
            'request': {
                'type': 'object',
                'properties': {
                    'prompt': {
                        'type': 'integer',
                        'nullable': True,
                        'description': 'GPT 프롬프트 ID (선택, 없으면 기본 대화)',
                    },
                    'message': {
                        'type': 'string',
                        'description': '첫 메시지 내용',
                        'example': '안녕하세요',
                    },
                    'model': {
                        'type': 'string',
                        'enum': ['gpt-4o-mini', 'gpt-4o', 'gpt-4o-turbo'],
                        'description': '사용할 GPT 모델',
                        'default': 'gpt-4o-mini',
                    },
                },
                'required': ['message'],
            },
            'responses': {
                200: {
                    'description': 'text/event-stream 스트리밍 응답',
                    'content': {
                        'text/event-stream': {
                            'schema': {
                                'type': 'string',
                                'description': 'GPT 응답 스트림 (SSE)',
                            }
                        }
                    }
                },
                400: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                OpenApiExample(
                    "Request Example",
                    summary="요청 예시",
                    description="채팅 시작 요청",
                    value={"prompt": 1, "message": "안녕하세요", "model": "gpt-4o-mini"},
                    request_only=True
                ),
                CommonExamples.error_example(
                    message="GPT 채팅 시작 실패",
                    errors={"message": ["이 필드는 blank일 수 없습니다."]}
                )
            ]
        }

    @staticmethod
    def get_gpt_session():
        return {
            'summary': "GPT 세션 스트리밍",
            'description': "프롬프트와 메시지로 GPT 응답을 스트리밍으로 받습니다. 채팅방/DB 저장 없이 세션만 수행합니다.",
            'operation_id': 'gpts_session_post',
            'request': {
                'type': 'object',
                'properties': {
                    'prompt': {
                        'type': 'integer',
                        'nullable': True,
                        'description': 'GPT 프롬프트 ID (선택, 없으면 기본 대화)',
                    },
                    'message': {
                        'type': 'string',
                        'description': '메시지 내용',
                        'example': '안녕하세요',
                    },
                    'model': {
                        'type': 'string',
                        'enum': ['gpt-4o-mini', 'gpt-4o', 'gpt-4o-turbo'],
                        'description': '사용할 GPT 모델',
                        'default': 'gpt-4o-mini',
                    },
                },
                'required': ['message'],
            },
            'responses': {
                200: {
                    'description': 'text/event-stream 스트리밍 응답',
                    'content': {
                        'text/event-stream': {
                            'schema': {
                                'type': 'string',
                                'description': 'GPT 응답 스트림 (SSE)',
                            }
                        }
                    }
                },
                400: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
            },
            'examples': [
                OpenApiExample(
                    "Request Example",
                    summary="요청 예시",
                    description="세션 스트리밍 요청",
                    value={"prompt": 1, "message": "안녕하세요", "model": "gpt-4o-mini"},
                    request_only=True
                ),
                CommonExamples.error_example(
                    message="GPT 세션 실패",
                    errors={"message": ["이 필드는 blank일 수 없습니다."]}
                )
            ]
        }
