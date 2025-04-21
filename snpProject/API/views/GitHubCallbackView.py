# API/views.py
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from social_django.models import UserSocialAuth
from galery.models import UserToken

class GitHubCallbackView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/login/')
            
        try:
            user_social = UserSocialAuth.objects.get(user=request.user, provider='github')
            user_token = UserToken.objects.get(user=request.user)
            
            response = HttpResponseRedirect('/')
            response.set_cookie(
                'access_token',
                user_token.access_token_hash,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=900,
                path='/',
            )
            response.set_cookie(
                'refresh_token',
                user_token.refresh_token_hash,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=604800,
                path='/',
            )
            return response
        except (UserSocialAuth.DoesNotExist, UserToken.DoesNotExist):
            return redirect('/login/')