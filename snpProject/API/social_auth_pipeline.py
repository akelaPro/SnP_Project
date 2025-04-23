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

    email = details.get('email')
    github_username = details.get('username')
    User = strategy.storage.user.user_model()

    # 1. Пытаемся найти существующего пользователя по email
    if email:
        try:
            user = User.objects.get(email=email)
            # Нашли пользователя - создаем токены и возвращаем его
            access_token, refresh_token = create_tokens_for_user(user)
            
            response = strategy.redirect('/')
            response.set_cookie('access_token', access_token, 
                              httponly=True, secure=not settings.DEBUG, 
                              samesite='Lax', max_age=900)
            response.set_cookie('refresh_token', refresh_token,
                              httponly=True, secure=not settings.DEBUG,
                              samesite='Lax', max_age=604800)
            
            return {
                'is_new': False,
                'user': user,
                'response': response
            }
        except User.DoesNotExist:
            pass  # Пользователя с таким email нет

    # 2. Если email не предоставлен или пользователь не найден
    # Генерируем уникальный username
    username = github_username
    if username:
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{github_username}_{counter}"
            counter += 1
    else:
        username = f"github_user_{secrets.token_hex(4)}"

    # 3. Создаем нового пользователя (без email если он уже занят)
    try:
        user = User.objects.create_user(
            username=username,
            email=email if email and not User.objects.filter(email=email).exists() else None,
            password=None
        )
    except IntegrityError:
        # Если все же возникла ошибка (редкий случай)
        user = User.objects.create_user(
            username=f"github_user_{secrets.token_hex(8)}",
            email=None,
            password=None
        )
    
    # Создаем токены
    access_token, refresh_token = create_tokens_for_user(user)
    
    response = strategy.redirect('/')
    response.set_cookie('access_token', access_token, 
                      httponly=True, secure=not settings.DEBUG,
                      samesite='Lax', max_age=900)
    response.set_cookie('refresh_token', refresh_token,
                      httponly=True, secure=not settings.DEBUG,
                      samesite='Lax', max_age=604800)
    
    return {
        'is_new': True,
        'user': user,
        'response': response
    }