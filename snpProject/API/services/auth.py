from django.contrib.auth import authenticate
from django.utils import timezone
from galery.models import UserToken
from API.utils import hash_token
import secrets
from .base import BaseService
from rest_framework import exceptions

class LoginService(BaseService):
    def process(self):
        username = self.data['username']
        password = self.data['password']
        
        user = authenticate(username=username, password=password)
        if not user:
            raise exceptions.AuthenticationFailed('Invalid credentials.')

        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        UserToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token_hash': hash_token(access_token),
                'refresh_token_hash': hash_token(refresh_token),
                'access_token_expires': timezone.now() + timezone.timedelta(minutes=2),
                'refresh_token_expires': timezone.now() + timezone.timedelta(days=7),
            }
        )

        return {
            'access': access_token,
            'refresh': refresh_token,
        }

class RefreshService(BaseService):
    def process(self):
        refresh_token = self.data['refresh_token']
        refresh_hash = hash_token(refresh_token)
        
        try:
            user_token = UserToken.objects.get(refresh_token_hash=refresh_hash)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid refresh token.')

        if timezone.now() > user_token.refresh_token_expires:
            raise exceptions.AuthenticationFailed('Refresh token expired.')

        new_access = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)

        user_token.access_token_hash = hash_token(new_access)
        user_token.refresh_token_hash = hash_token(new_refresh)
        user_token.access_token_expires = timezone.now() + timezone.timedelta(minutes=2)
        user_token.refresh_token_expires = timezone.now() + timezone.timedelta(days=7)
        user_token.save()

        return {
            'access': new_access,
            'refresh': new_refresh,
        }

class LogoutService(BaseService):
    def process(self):
        user = self.data['user']
        try:
            user.token.delete()
        except:
            pass