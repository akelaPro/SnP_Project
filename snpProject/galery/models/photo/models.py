from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
import os
from django.utils import timezone
from snpProject import settings
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def upload_to(instance, filename):
    """
    Функция для формирования пути сохранения файла на основе ID.
    Этот путь используется только после того, как ID будет известен.
    """
    return f'photos/{instance.pk}/{filename}'

class Photo(models.Model):
    STATUS_CHOICES = (
        ('1', 'На удалении'),
        ('2', 'На модерации'),
        ('3', 'Одобрено'),
        ('4', 'Отклонено'),
    )

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='temp_photos/', default=None, blank=True, null=False, verbose_name='Фотография') # Временно сохраняем в temp_photos
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
        """Удаляет старую фотографию из хранилища S3."""
        if self.old_image:
        # Удаляем файл из S3
            self.old_image.delete(save=False)
            self.old_image = None
            self.save()

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def save(self, *args, **kwargs):
        if self.pk is None:  # Новый объект
            # 1. Получаем временное имя файла
            temp_image = self.image
            self.image = None  # Очищаем поле image, чтобы не сохранять его сейчас
            super().save(*args, **kwargs)  # Сохраняем, чтобы получить ID (pk)
            # 2. Генерируем новое имя файла с pk
            new_filename = upload_to(self, temp_image.name)
            # 3. Читаем содержимое файла из временного хранилища
            if hasattr(temp_image, 'read'):
                file_content = temp_image.read()
            else:
                # Если temp_image не имеет метода read, обрабатываем его как FilePathField или что-то подобное
                with open(temp_image.path, 'rb') as f:
                    file_content = f.read()
            # 4. Сохраняем файл в нужное место с новым именем
            self.image.name = new_filename
            default_storage.save(self.image.name, ContentFile(file_content))
            # 5. Сохраняем модель еще раз, чтобы обновить поле image
            super().save(update_fields=['image'])

            # Удаляем временный файл (необязательно, зависит от вашей конфигурации)
            default_storage.delete(temp_image.name)
        else:  # Существующий объект
            old = Photo.objects.get(pk=self.pk)
            if old.image != self.image:
                if old.image:
                    self.old_image = old.image
            super().save(*args, **kwargs)


@receiver(post_save, sender=Photo)
def handle_photo_moderation(sender, instance, **kwargs):
    """
    Удаляет старое изображение после одобрения новой фотографии.
    """
    if instance.moderation == '3' and instance.old_image:
        instance.delete_old_image()