from django.db import models
from django.urls import reverse
from snpProject import settings


class Photo(models.Model):

    STATUS_CHOICES = (
        ('1', 'На удалении'),
        ('2', 'На модерации'),
        ('3', 'Одобренно'),
        ('4', 'отклонено'),
    )

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=False, verbose_name='Фотография')  
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=4, related_name='photos')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')
    moderation = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="Статус", default='2')
    old_image = models.ImageField(upload_to='photos/old/', blank=True, null=True, verbose_name='Старая фотография')
    deleted_at = models.DateTimeField(null=True, blank=True)


    def get_absolute_url(self):
        return reverse('photo_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'