from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from snpProject import settings
import logging
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def upload_to(instance, filename):
    """Генерирует уникальное имя файла с ID фотографии и оригинальным именем"""
    ext = os.path.splitext(filename)[1]  # получаем расширение файла
    return f'photos/{instance.pk}/photo_{instance.pk}{ext}'

class Photo(models.Model):
    STATUS_CHOICES = (
        ('1', 'На удалении'),
        ('2', 'На модерации'),
        ('3', 'Одобрено'),
        ('4', 'Отклонено'),
    )

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='temp_photos/', verbose_name='Фотография')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              related_name='photos', verbose_name='Автор', db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления', db_index=True)
    moderation = models.CharField(max_length=1, choices=STATUS_CHOICES, 
                                verbose_name="Статус", default='2', db_index=True)
    old_image = models.ImageField(upload_to='photos/old/%Y/%m/%d/', 
                                blank=True, null=True, verbose_name='Старая фотография')
    delete_task_id = models.CharField(max_length=255, null=True, blank=True, 
                                    verbose_name="ID задачи удаления")

    def __str__(self):
        return self.title

    def get_moderation_display(self):
        return dict(self.STATUS_CHOICES).get(self.moderation, 'Неизвестный статус')

    def delete_old_image(self):
        """Удаляет старую фотографию из хранилища"""
        if self.old_image:
            self.old_image.delete(save=False)
            self.old_image = None
            self.save()

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new:
            # Сохраняем временный файл
            temp_image = self.image
            self.image = None
            super().save(*args, **kwargs)  # Получаем ID
            
            # Генерируем новое имя файла
            new_path = upload_to(self, temp_image.name)
            
            # Переносим файл из временного хранилища
            if hasattr(temp_image, 'temporary_file_path'):
                # Для временных загруженных файлов
                with open(temp_image.temporary_file_path(), 'rb') as f:
                    default_storage.save(new_path, f)
                os.unlink(temp_image.temporary_file_path())
            else:
                # Для других случаев
                file_content = temp_image.read()
                default_storage.save(new_path, ContentFile(file_content))
            
            # Обновляем поле image
            self.image.name = new_path
            kwargs['force_insert'] = False
            super().save(update_fields=['image'])
            
            # Удаляем временный файл
            if default_storage.exists(temp_image.name):
                default_storage.delete(temp_image.name)
        else:
            old = Photo.objects.get(pk=self.pk)
            if old.image != self.image:
                if old.image:
                    self.old_image = old.image
            super().save(*args, **kwargs)


@receiver(post_save, sender=Photo)
def handle_photo_moderation(sender, instance, **kwargs):
    """Удаляет старое изображение после одобрения новой фотографии"""
    if instance.moderation == '3' and instance.old_image:
        instance.delete_old_image()