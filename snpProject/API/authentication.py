from datetime import timedelta
from rest_framework import authentication, exceptions
from django.utils.translation import gettext_lazy as _
from galery.models import *
from .utils import hash_token
from django.utils import timezone
import logging
from django.contrib.auth.backends import BaseBackend


logger = logging.getLogger(__name__)

class CustomTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Try to get token from both cookies and headers
        access_token = (
            request.COOKIES.get('access_token') or 
            request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
        )
        
        if not access_token:
            return None

        return self.authenticate_credentials(access_token)

    def authenticate_credentials(self, token):
        try:
            access_hash = hash_token(token)
            user_token = UserToken.objects.select_related('user').get(
                access_token_hash=access_hash,
                access_token_expires__gt=timezone.now()
            )
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid or expired token.'))

        # Auto-refresh token if near expiration
        if user_token.access_token_expires - timezone.now() < timedelta(minutes=5):
            self.refresh_token(user_token)

        return (user_token.user, None)
    
