from django.db import models
from django.conf import settings
from django.utils import timezone

def get_default_access_expires():
    return timezone.now() + timezone.timedelta(minutes=2)  # Access token expires in 2 minutes

def get_default_refresh_expires():
    return timezone.now() + timezone.timedelta(days=7)

class UserToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='token'
    )
    access_token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    access_token_expires = models.DateTimeField(default=get_default_access_expires)
    refresh_token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    refresh_token_expires = models.DateTimeField(default=get_default_refresh_expires)