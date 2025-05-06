from venv import logger
from django.contrib.auth import authenticate
from django.utils import timezone
from galery.models import UserToken
from API.utils import hash_token
import secrets
from .base import BaseService
from rest_framework import exceptions


#logger.info(f"Refreshing tokens for user {UserToken.user.id}")

class LoginService:
    @classmethod
    def execute(cls, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise exceptions.ValidationError("Email и пароль обязательны")
        
        user = authenticate(username=email, password=password)
        if not user:
            raise exceptions.AuthenticationFailed('Неверные учетные данные')

        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        UserToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token_hash': hash_token(access_token),
                'refresh_token_hash': hash_token(refresh_token),
                'access_token_expires': timezone.now() + timezone.timedelta(minutes=15),
                'refresh_token_expires': timezone.now() + timezone.timedelta(days=7),
            }
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user
        }