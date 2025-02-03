from django.db import models
from django.urls import reverse
from snpProject import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Photo(models.Model):
    STATUS_CHOICES = (
        ('1', 'На удалении'),
        ('2', 'На модерации'),
        ('3', 'Одобрено'),
        ('4', 'отклонено'),
    )

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=False, verbose_name='Фотография')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='photos', verbose_name='Автор', db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления', db_index=True)
    moderation = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="Статус", default='2', db_index=True)
    old_image = models.ImageField(upload_to='photos/old/', blank=True, null=True, verbose_name='Старая фотография')

  
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 60}
    )

    def get_absolute_url(self):
        return reverse('photo_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
