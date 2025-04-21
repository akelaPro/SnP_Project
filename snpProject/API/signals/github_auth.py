# galery/social_auth_signals.py
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model
from django.utils import timezone
from API.utils import hash_token
import secrets
from galery.models import UserToken
from django.contrib.auth import login
from importlib import import_module
from django.conf import settings
from django.contrib.auth.hashers import make_password


from django.db.models.signals import post_save
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model
from django.utils import timezone
from API.utils import hash_token
import secrets
from galery.models import UserToken
from django.contrib.auth.hashers import make_password



@receiver(post_save, sender=UserSocialAuth)
def handle_github_auth(sender, instance, created, **kwargs):
    if instance.provider != 'github':
        return

    user = instance.user
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)

    UserToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token_hash': hash_token(access_token),
            'refresh_token_hash': hash_token(refresh_token),
            'access_token_expires': timezone.now() + timedelta(minutes=15),
            'refresh_token_expires': timezone.now() + timedelta(days=7)
        }
    )
    
    # Сохраняем токены в сессии для последующего использования в middleware
    from django.contrib.sessions.backends.db import SessionStore
    session = SessionStore()
    session['github_auth_tokens'] = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    session.save()