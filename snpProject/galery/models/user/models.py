from django.db import models
from django.contrib.auth.models import AbstractUser  
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class User(AbstractUser ):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')
    updated_at = models.DateTimeField(auto_now=True)

    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(100, 100)],  # Уменьшение до 100x100 пикселей
        format='PNG',
        options={'quality': 60}
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
