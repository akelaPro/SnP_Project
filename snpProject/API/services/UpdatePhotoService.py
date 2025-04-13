from galery.models import Photo
from django.utils import timezone
from django.db import transaction
from .base import BaseService
from API.task import delete_photo
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)


class UpdatePhotoService(BaseService):
    def process(self):
        instance = self.data['photo']
        user = self.data['user']
        serializer_class = self.data['serializer_class']  # Получаем класс сериализатора из данных
        request = self.data['request']
    
        if instance.author != user:
            raise exceptions.PermissionDenied("Вы не можете изменять эту фотографию.")
        
        with transaction.atomic():
            # Lock the instance for update
            instance = Photo.objects.select_for_update().get(pk=instance.id)
            
            # Используем переданный serializer_class вместо вызова несуществующего метода
            serializer = serializer_class(
                instance, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            
            # Refresh from database to ensure we have latest version
            instance.refresh_from_db()
        
            self.notify_user(
                user=instance.author,
                message=f"Фотография '{instance.title}' успешно обновлена.",
                notification_type='photo_updated'
            )
            
            return instance