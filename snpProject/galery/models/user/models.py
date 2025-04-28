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
    first_name = models.CharField(max_length=150, verbose_name='Имя', blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')
    updated_at = models.DateTimeField(auto_now=True)
    password_reset_token_hash = models.CharField(max_length=64, null=True, blank=True)
    password_reset_token_expires = models.DateTimeField(null=True, blank=True)

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




