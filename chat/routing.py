from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_id>[0-9a-fA-F-]+)/$", consumers.ChatConsumer.as_asgi()),
    re_path("ws/chat-list/", consumers.ChatListConsumer.as_asgi()),
    re_path(r"ws/guide/transactions/$", consumers.GuideTransactionConsumer.as_asgi()),

]
