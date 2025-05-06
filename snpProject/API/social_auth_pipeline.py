import logging
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from galery.models import UserToken
from datetime import timedelta
from django.utils import timezone
from API.utils import hash_token
import secrets
from django.conf import settings
from django.shortcuts import redirect


logger = logging.getLogger(__name__)

def create_tokens_for_user(user):
    # Генерируем случайные строки для токенов
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    
    # Создаем или обновляем запись токенов для пользователя
    UserToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token_hash': hash_token(access_token),
            'refresh_token_hash': hash_token(refresh_token),
            'access_token_expires': timezone.now() + timedelta(minutes=15),
            'refresh_token_expires': timezone.now() + timedelta(days=7)
        }
    )
    
    return access_token, refresh_token

def get_or_create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False, 'user': user}

    try:
        email = details.get('email')
        github_username = details.get('username')
        User = strategy.storage.user.user_model()

        # Поиск или создание пользователя
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = github_username or f"github_{secrets.token_hex(4)}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None
                )
        else:
            username = github_username or f"github_{secrets.token_hex(8)}"
            user = User.objects.create_user(
                username=username,
                email=None,
                password=None
            )

        # Создание токенов
        access_token, refresh_token = create_tokens_for_user(user)
        
        # Создание ответа с куками
        response = HttpResponseRedirect('/')
        response.set_cookie(
            'access_token', 
            access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=900
        )
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=604800
        )
        
        # Удаление сессионных куков, если они есть
        if 'sessionid' in response.cookies:
            del response.cookies['sessionid']
        if 'csrftoken' in response.cookies:
            del response.cookies['csrftoken']

        return {
            'is_new': True,
            'user': user,
            'response': response
        }

    except Exception as e:
        logger.error(f"Error in social auth pipeline: {str(e)}")
        return strategy.redirect(f'/?error=auth_failed&message={str(e)}')