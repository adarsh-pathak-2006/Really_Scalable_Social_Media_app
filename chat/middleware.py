from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token')
        
        if token:
            try:
                UntypedToken(token[0])
                decoded_data = UntypedToken(token[0]).payload
                scope['user'] = await get_user(decoded_data['user_id'])
            except (InvalidToken, TokenError, KeyError):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
