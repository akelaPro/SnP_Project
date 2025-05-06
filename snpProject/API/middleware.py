from django.conf import settings
from API.social_auth_pipeline import create_tokens_for_user


class SocialAuthCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Если это запрос от social auth и есть пользователь
        if '/social-auth/' in request.path and hasattr(request, 'user'):
            if request.user.is_authenticated:
                access_token, refresh_token = create_tokens_for_user(request.user)
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
        return response