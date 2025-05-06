from API.serializers.photos import PhotoSerializer
from galery.models import Photo
from django.utils import timezone
from django.db import transaction
from .base import BaseService
from API.task import delete_photo
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)


# API/services.py
class UpdatePhotoService(BaseService):
    def process(self):
        instance = self.data['photo']
        user = self.data['user']
        request = self.data['request']

        if instance.author != user:
            raise exceptions.PermissionDenied("Вы не можете изменять эту фотографию.")

        serializer = PhotoSerializer(
            instance,
            data=request.data,
            partial=True,  # Разрешаем частичное обновление
            context={'request': request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                # Lock the instance for update
                instance = Photo.objects.select_for_update().get(pk=instance.id)
                instance = serializer.save()
                instance.refresh_from_db()  # Ensure you have the latest version

            self.notify_user(
                user=instance.author,
                message=f"Фотография '{instance.title}' успешно обновлена.",
                notification_type='photo_updated'
            )
            return instance
        else:
            # Обработка ошибок валидации
            print(serializer.errors) # Логируем ошибки
            raise exceptions.ValidationError(serializer.errors)