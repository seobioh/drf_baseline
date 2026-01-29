# gpts/urls.py
app_name = "gpts"

from django.urls import path

from .views import GPTPromptAPIView, GPTChatRoomAPIView, GPTChatRoomDetailAPIView, GPTChatMessageAPIView, GPTStartAPIView
from .views import GPTSessionAPIView

urlpatterns = [
    path('/prompts', GPTPromptAPIView.as_view(), name='gpt_prompts'),
    path('/chatrooms', GPTChatRoomAPIView.as_view(), name='gpt_chat_rooms'),
    path('/chatrooms/<int:gpt_chat_room_id>', GPTChatRoomDetailAPIView.as_view(), name='gpt_chat_room_detail'),
    path('/chatrooms/<int:gpt_chat_room_id>/messages', GPTChatMessageAPIView.as_view(), name='gpt_chat_messages'),
    path('/start', GPTStartAPIView.as_view(), name='gpt_start'),
    
    path('/session', GPTSessionAPIView.as_view(), name='gpt_session'),
]