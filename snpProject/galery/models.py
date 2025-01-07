from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.contrib.auth import get_user_model
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from viewflow.workflow.models import Process
from snpProject import settings
from viewflow import jsonstore


class Photo(models.Model):

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=False, verbose_name='Фотография')  
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=4, related_name='photos')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрено')

    def get_absolute_url(self):
        return reverse('photo_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'


class PhotoModerationProcess(Process):
    photo = models.OneToOneField('Photo', on_delete=models.CASCADE, null=False)  
    approved = jsonstore.BooleanField(default=False)
    rejected = jsonstore.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.approved and not self.photo.is_approved:
            self.photo.is_approved = True
            self.photo.save()
        elif self.rejected and self.photo.is_approved:
            self.photo.is_approved = False
            self.photo.save()




    def __str__(self):
        return f"Moderation for {self.photo.title}"






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