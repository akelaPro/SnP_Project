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
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None

        return self.authenticate_credentials(access_token)

    def authenticate_credentials(self, token):
        access_hash = hash_token(token)
        try:
            user_token = UserToken.objects.select_related('user').get(access_token_hash=access_hash)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if timezone.now() > user_token.access_token_expires:
            raise exceptions.AuthenticationFailed(_('Token has expired.'))

        # Обновляем время жизни токена только если осталось меньше минуты
        if user_token.access_token_expires - timezone.now() < timedelta(minutes=1):
            user_token.access_token_expires = timezone.now() + timedelta(minutes=15)
            user_token.save(update_fields=['access_token_expires'])

        return (user_token.user, None)
    
