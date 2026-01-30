# gpts/views.py
app_name = "gpts"

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from server.utils import SuccessResponseBuilder, ErrorResponseBuilder

from .models import GPTPrompt, GPTChatRoom, GPTChatMessage
from .paginations import GPTChatMessagePagination
from .permissions import IsAuthenticated, IsGPTChatRoomOwner
from .serializers import GPTPromptSerializer, GPTChatRoomSerializer, GPTChatMessageSerializer
from .schemas import GPTSchema
from .utils import GPTService, GPTSessionService

class GPTPromptAPIView(APIView):
    @extend_schema(**GPTSchema.get_gpt_prompts())
    def get(self, request):
        gpt_prompts = GPTPrompt.objects.filter(is_active=True)
        serializer = GPTPromptSerializer(gpt_prompts, many=True)
        response = SuccessResponseBuilder().with_message("GPT 프롬프트 조회 성공").with_data({"gpt_prompts": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)
    

class GPTChatRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(**GPTSchema.get_gpt_chat_rooms())
    def get(self, request):
        gpt_chat_rooms = GPTChatRoom.objects.filter(user=request.user, is_active=True)
        serializer = GPTChatRoomSerializer(gpt_chat_rooms, many=True)
        response = SuccessResponseBuilder().with_message("GPT 채팅방 조회 성공").with_data({"gpt_chat_rooms": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(**GPTSchema.create_gpt_chat_room())
    def post(self, request):
        serializer = GPTChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            response = SuccessResponseBuilder().with_message("GPT 채팅방 생성 성공").with_data({"gpt_chat_room": serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = ErrorResponseBuilder().with_message("GPT 채팅방 생성 실패").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GPTChatRoomDetailAPIView(APIView):
    permission_classes = [IsGPTChatRoomOwner]

    @extend_schema(**GPTSchema.get_gpt_chat_room_detail())
    def get(self, request, gpt_chat_room_id):
        gpt_chat_room = get_object_or_404(GPTChatRoom, id=gpt_chat_room_id, is_active=True)
        self.check_object_permissions(request, gpt_chat_room)
        serializer = GPTChatRoomSerializer(gpt_chat_room)
        response = SuccessResponseBuilder().with_message("GPT 채팅방 상세 조회 성공").with_data({"gpt_chat_room": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(**GPTSchema.update_gpt_chat_room())
    def put(self, request, gpt_chat_room_id):
        gpt_chat_room = get_object_or_404(GPTChatRoom, id=gpt_chat_room_id, is_active=True)
        self.check_object_permissions(request, gpt_chat_room)
        serializer = GPTChatRoomSerializer(gpt_chat_room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = SuccessResponseBuilder().with_message("GPT 채팅방 수정 성공").with_data({"gpt_chat_room": serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = ErrorResponseBuilder().with_message("GPT 채팅방 수정 실패").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(**GPTSchema.delete_gpt_chat_room())
    def delete(self, request, gpt_chat_room_id):
        gpt_chat_room = get_object_or_404(GPTChatRoom, id=gpt_chat_room_id, is_active=True)
        self.check_object_permissions(request, gpt_chat_room)
        gpt_chat_room.delete()
        response = SuccessResponseBuilder().with_message("GPT 채팅방 삭제 성공").build()
        return Response(response, status=status.HTTP_200_OK)


class GPTChatMessageAPIView(APIView):
    permission_classes = [IsGPTChatRoomOwner]
    pagination_class = GPTChatMessagePagination

    @extend_schema(**GPTSchema.get_gpt_chat_message_detail())
    def get(self, request, gpt_chat_room_id):
        gpt_chat_room = get_object_or_404(GPTChatRoom, id=gpt_chat_room_id, is_active=True)
        self.check_object_permissions(request, gpt_chat_room)
        messages = GPTChatMessage.objects.filter(chat_room=gpt_chat_room).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request, view=self)
        if page is not None:
            pagination = {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'page_size': paginator.page_size,
            }
            serializer = GPTChatMessageSerializer(page, many=True)
            response = SuccessResponseBuilder().with_message("GPT 채팅메시지 조회 성공").with_data({"gpt_chat_messages": serializer.data, "pagination": pagination}).build()
        else:
            serializer = GPTChatMessageSerializer(messages, many=True)
            response = SuccessResponseBuilder().with_message("GPT 채팅메시지 조회 성공").with_data({"gpt_chat_messages": serializer.data}).build()
        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(**GPTSchema.create_gpt_chat_message())
    def post(self, request, gpt_chat_room_id):
        gpt_chat_room = get_object_or_404(GPTChatRoom, id=gpt_chat_room_id, is_active=True)
        self.check_object_permissions(request, gpt_chat_room)
        serializer = GPTChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chat_room=gpt_chat_room, role='user')
            gpt_service = GPTService(gpt_chat_room)

            response = StreamingHttpResponse(gpt_service.stream(serializer.instance), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
        else:
            response = ErrorResponseBuilder().with_message("GPT 채팅메시지 생성 실패").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GPTStartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**GPTSchema.start_gpt())
    def post(self, request):
        prompt_id = request.data.get("prompt")
        message = request.data.get("message")
        model = request.data.get("model", "gpt-4o-mini")

        prompt = None
        if prompt_id:
            prompt = get_object_or_404(GPTPrompt, id=prompt_id, is_active=True)

        chat_room = GPTChatRoom.objects.create(user=request.user, prompt=prompt)
        user_msg = GPTChatMessage.objects.create(chat_room=chat_room, role="user", model=model, message=message,)
        gpt_service = GPTService(chat_room)

        response = StreamingHttpResponse(gpt_service.stream_with_init(user_msg), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class GPTSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**GPTSchema.get_gpt_session())
    def post(self, request):
        prompt_id = request.data.get("prompt")
        message = request.data.get("message")
        model = request.data.get("model", "gpt-4o-mini")

        prompt = None
        if prompt_id:
            prompt = get_object_or_404(GPTPrompt, id=prompt_id, is_active=True)

        gpt_session_service = GPTSessionService(model=model, prompt=prompt)
        response = StreamingHttpResponse(gpt_session_service.stream(message), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response