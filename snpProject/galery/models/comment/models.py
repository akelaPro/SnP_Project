from django.db import models
from galery.models.photo.models import Photo
from galery.models.user.models import User
from django.core.exceptions import ValidationError


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор', db_index=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments', verbose_name='Фото', db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='Ответ на', db_index=True)

    def __str__(self):
        return f"Comment by {self.author.email} on {self.photo.title}"

    def clean(self):
        if self.parent and self.parent.photo != self.photo:
            raise ValidationError("Ответ должен быть к тому же фото.")

    def can_delete(self):
        """Проверяет, может ли комментарий быть удален."""
        return not self.replies.exists()  # У комментa нет ответов
        # or (self.parent is not None and not self.replies.exists())  # Коммент является ответом и нет ответов на него

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ['-created_at']