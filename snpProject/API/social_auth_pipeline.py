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

def create_auth_tokens(strategy, backend, user, response, *args, **kwargs):
    if not user.is_authenticated:
        return
    
    access_token, refresh_token = create_tokens_for_user(user)
    
    # Get the existing response or create new one
    if not isinstance(response, HttpResponseRedirect):
        response = strategy.redirect('/')
    
    # Set cookies with proper domain/path
    domain = None if settings.DEBUG else '.yourdomain.com'
    
    response.set_cookie(
        'access_token', 
        access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=900,  # 15 minutes
        domain=domain,
        path='/'
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=604800,  # 7 days
        domain=domain,
        path='/'
    )
    
    return {'response': response}


def get_or_create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False, 'user': user}

    email = details.get('email')
    github_username = details.get('username')
    User = strategy.storage.user.user_model()

    try:
        if email:
            user = User.objects.get(email=email)
            return {'is_new': False, 'user': user}
    except User.DoesNotExist:
        pass

    # Create new user
    username = github_username or f"github_{secrets.token_hex(8)}"
    while User.objects.filter(username=username).exists():
        username = f"{username}_{secrets.token_hex(2)}"

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=None
        )
    except IntegrityError:
        user = User.objects.create_user(
            username=f"github_{secrets.token_hex(12)}",
            email=None,
            password=None
        )

    return {'is_new': True, 'user': user}