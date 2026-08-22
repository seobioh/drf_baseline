# gpts/serializers.py
app_name = "gpts"

from rest_framework import serializers

from .models import GPTPrompt, GPTChatRoom, GPTChatMessage, GPTEmbeddingCategory, GPTEmbedding

class GPTPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPTPrompt
        fields = ['id', 'name', 'description', 'created_at', 'modified_at']
        read_only_fields = ['id', 'name', 'description', 'created_at', 'modified_at']


class GPTChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPTChatRoom
        fields = ['id', 'name', 'user', 'prompt', 'summary', 'summary_token_count', 'last_summarized_message', 'created_at', 'modified_at']
        read_only_fields = ['id', 'user', 'summary', 'summary_token_count', 'last_summarized_message', 'created_at', 'modified_at']


class GPTChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPTChatMessage
        fields = ['id', 'chat_room', 'role', 'model', 'message', 'token_count', 'is_error', 'created_at']
        read_only_fields = ['id', 'chat_room', 'role', 'token_count', 'is_error', 'created_at']


class GPTEmbeddingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GPTEmbeddingCategory
        fields = ['id', 'name', 'description', 'embedding_model', 'prompt', 'is_active', 'created_at', 'modified_at']
        read_only_fields = ['id', 'created_at', 'modified_at']


class GPTEmbeddingSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    embedding_model = serializers.CharField(source='category.embedding_model', read_only=True)

    class Meta:
        model = GPTEmbedding
        fields = ['id', 'category', 'category_name', 'title', 'content', 'embedding_model', 'is_active', 'created_at', 'modified_at']
        read_only_fields = ['id', 'category_name', 'embedding_model', 'created_at', 'modified_at']