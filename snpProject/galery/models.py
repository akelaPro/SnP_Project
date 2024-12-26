from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.contrib.auth import get_user_model
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill



class Photo(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True, verbose_name='Фотография')  
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey('galery.User', on_delete=models.SET_NULL, null=True, related_name='photos' , verbose_name='Автор')

    def get_absolute_url(self):
        return reverse('photo_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    avatar_thumbnail = ImageSpecField(source='avatar',
                                       processors=[ResizeToFill(100, 100)],
                                       format='JPEG',
                                       options={'quality': 60})


    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'



class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes', verbose_name='Автор')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='votes', verbose_name='Фотография')


    class Meta:
        unique_together = ('author', 'photo')

    def __str__(self):
        return f"{self.author.email} voted for {self.photo.title}"
    

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments', verbose_name='Фото')

    def __str__(self):
        return f"Comment by {self.author.email} on {self.photo.title}"
    

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'