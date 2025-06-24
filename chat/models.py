from django.db import models
from django.contrib.auth import get_user_model
from authentications.models import UserProfile, GuideProfile
import uuid
from django.conf import settings

User = get_user_model()

class ChatHistory(models.Model):
    chat_id = models.UUIDField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Chat {self.chat_id}"

class ChatMessage(models.Model):
    chat = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', blank=True, null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages' , blank=True, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.sender.email} to {self.receiver.email}: {self.message[:20]}"

    class Meta:
        ordering = ['timestamp']