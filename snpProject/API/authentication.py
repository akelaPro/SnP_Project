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
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed(_('Invalid token header.'))

        token = auth[1].decode()
        return self.authenticate_credentials(token)

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
            user_token.access_token_expires = timezone.now() + timezone.timedelta(minutes=2)
            user_token.save(update_fields=['access_token_expires'])

        return (user_token.user, None)
    
class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and user.is_active:
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None