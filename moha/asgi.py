import os
import django  # ✅ Import Django first
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# ✅ Ensure Django settings are loaded before anything else
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moha.settings")
django.setup()  # ✅ Required to load Django apps properly

import chat.routing  # ✅ Now it's safe to import after `django.setup()`

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # ✅ Standard HTTP requests
    "websocket": URLRouter(chat.routing.websocket_urlpatterns),  # ✅ WebSocket routes (No authentication required)
})
