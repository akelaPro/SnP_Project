from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
import os

from snpProject import settings
import logging

logger = logging.getLogger(__name__)

class Photo(models.Model):
    STATUS_CHOICES = (
        ('1', 'На удалении'),
        ('2', 'На модерации'),
        ('3', 'Одобрено'),
        ('4', 'Отклонено'),
    )

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=False, verbose_name='Фотография')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='photos', verbose_name='Автор', db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления', db_index=True)
    moderation = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="Статус", default='2', db_index=True)
    old_image = models.ImageField(upload_to='photos/old/%Y/%m/%d/', blank=True, null=True, verbose_name='Старая фотография')
    delete_task_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID задачи удаления")

    def __str__(self):
        return self.title

    def get_moderation_display(self):
        return dict(self.STATUS_CHOICES).get(self.moderation, 'Неизвестный статус')

    def delete_old_image(self):
        """Удаляет старую фотографию из файловой системы."""
        if self.old_image:
            if os.path.isfile(self.old_image.path):
                os.remove(self.old_image.path)
            self.old_image = None
            self.save()

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def save(self, *args, **kwargs):
        if self.pk:  # Если объект уже существует
            old = Photo.objects.get(pk=self.pk)
            if old.image != self.image:  # Если изображение изменилось
            # Сохраняем старое изображение
                if old.image:
                    self.old_image = old.image
            if old.moderation != self.moderation or old.deleted_at != self.deleted_at:
                logger.info(
                    f"Изменение статуса фото {self.id}: "
                    f"moderation {old.moderation}->{self.moderation}, "
                    f"deleted_at {old.deleted_at}->{self.deleted_at}"
                )
        super().save(*args, **kwargs) 

@receiver(post_save, sender=Photo)
def handle_photo_moderation(sender, instance, **kwargs):
    """
    Удаляет старое изображение после одобрения новой фотографии.
    """
    if instance.moderation == '3' and instance.old_image:
        instance.delete_old_image()