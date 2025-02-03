from django.db import models
from galery.models.photo.models import Photo
from galery.models.user.models import User


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор', db_index=True) # добавил db_index
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments', verbose_name='Фото', db_index=True) # добавил db_index

    def __str__(self):
        return f"Comment by {self.author.email} on {self.photo.title}"
    

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'