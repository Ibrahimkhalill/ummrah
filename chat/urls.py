# chat/urls.py
from django.urls import path
from . import views

print("Loading chat/urls.py")  # Debug print to confirm file is loaded

urlpatterns = [
    path('history/<str:chat_id>/', views.chat_history, name='chat_history'),
    path('start/', views.start_chat, name='start_chat'),
    path('user-chat-list/', views.user_chat_list, name='user_chat_list'),
    path('mark-read/<str:chat_id>/', views.mark_chat_messages_as_read, name='mark_chat_messages_as_read'),
    path('count/unread/', views.count_unread_messages, name='count/unread/'),
]