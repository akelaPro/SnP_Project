import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser  
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.db.models.signals import post_save
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from API.utils import hash_token
from galery.models.customToken.models import UserToken


class User(AbstractUser ):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')
    updated_at = models.DateTimeField(auto_now=True)

    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(100, 100)], 
        format='PNG',
        options={'quality': 60}
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


@receiver(post_save, sender=UserSocialAuth)
def create_or_update_user(sender, instance, created, **kwargs):
    breakpoint()
    github_user = instance.extra_data
    username = github_user.get('login')
    email = github_user.get('email')
    name = github_user.get('name')
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'first_name': name, 'password':'password'}
) 
    token = UserToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token_hash': hash_token(access_token),
            'refresh_token_hash': hash_token(refresh_token),
            'access_token_expires': timezone.now() + timezone.timedelta(minutes=2),
            'refresh_token_expires': timezone.now() + timezone.timedelta(days=7),
        }
    ) 
    

