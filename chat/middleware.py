from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware.base import BaseMiddleware
from rest_framework.authtoken.models import Token

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user  # ✅ Return the authenticated user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """Custom middleware to authenticate WebSocket connections using token authentication."""

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token", [None])[0]  # ✅ Extract token from query params
        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)
