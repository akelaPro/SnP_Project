from django.db import models
from django.contrib.auth.models import AbstractUser 


class Photo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True)  
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='photos')

    def __str__(self):
        return self.title


class User(AbstractUser ):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.email




class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return f"{self.author.email} voted for {self.photo.title}"


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.author.email} on {self.photo.title}"