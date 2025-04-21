# galery/social_auth_signals.py
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
def create_or_update_user(sender, instance, created, **kwargs):
    if instance.provider != 'github':
        return

    github_user = instance.extra_data
    User = get_user_model()
    username = github_user.get('login')
    email = github_user.get('email') or f"{username}@github.com"
    name = github_user.get('name', '').split() or [username]

    user, user_created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': name[0],
            'last_name': name[1] if len(name) > 1 else '',
            'password': make_password(None)
        }
    )

    if user_created:
        user.set_unusable_password()
        user.save()

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