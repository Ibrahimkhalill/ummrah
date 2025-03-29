from django.contrib import admin
from .models import ChatHistory, ChatMessage
# Register your models here.
admin.site.register(ChatHistory)
admin.site.register(ChatMessage)