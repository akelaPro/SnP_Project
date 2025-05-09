from django.db import models
from galery.models.user.models import User
from galery.models.photo.models import Photo


class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes', verbose_name='Автор', db_index=True) # добавил db_index
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='votes', verbose_name='Фотография', db_index=True) # добавил db_index


    class Meta:
        unique_together = ('author', 'photo')

    def __str__(self):
        return f"{self.author.email} voted for {self.photo.title}"
    

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('author', 'photo')