from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class GitHubAuthMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'session') and 'github_auth_tokens' in request.session:
            tokens = request.session.pop('github_auth_tokens')
            
            response.set_cookie(
                'access_token',
                tokens['access_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=900
            )
            response.set_cookie(
                'refresh_token',
                tokens['refresh_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=604800
            )
        return response