from rest_framework import serializers
from .models import ChatHistory, ChatMessage

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id','chat_id', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'sender', 'receiver', 'message', 'timestamp', 'is_read']