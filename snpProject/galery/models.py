from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.contrib.auth import get_user_model
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Photo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True)  
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('galery.User', on_delete=models.SET_NULL, null=True, related_name='photos')

    def get_absolute_url(self):
        return reverse('photo_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default_avatar.png', blank=True, null=True)
    

    avatar_thumbnail = ImageSpecField(source='avatar',
                                       processors=[ResizeToFill(100, 100)],
                                       format='JPEG',
                                       options={'quality': 60})


    def __str__(self):
        return self.email




class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='votes')


    class Meta:
        unique_together = ('author', 'photo')

    def __str__(self):
        return f"{self.author.email} voted for {self.photo.title}"


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.author.email} on {self.photo.title}"