# API/views.py
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from social_django.models import UserSocialAuth
from galery.models import UserToken
from API.utils import hash_token
import secrets
from django.utils import timezone


class GitHubCallbackView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            # Пользователь уже аутентифицирован
            return redirect('/')
            
        try:
            user_social = UserSocialAuth.objects.get(user=request.user, provider='github')
            user = user_social.user
            
            # Создаем токены
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
            
            # Выполняем вход
            login(request, user)
            
            response = HttpResponseRedirect('/')
            response.set_cookie(
                'access_token',
                access_token,  # Устанавливаем сам токен, а не его хеш
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=900,
                path='/',
            )
            response.set_cookie(
                'refresh_token',
                refresh_token,  # Устанавливаем сам токен, а не его хеш
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=604800,
                path='/',
            )
            return response
        except (UserSocialAuth.DoesNotExist, UserToken.DoesNotExist):
            return redirect('/login/')