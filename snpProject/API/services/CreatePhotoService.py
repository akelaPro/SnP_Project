from galery.models import Photo
from django.utils import timezone
from django.db import transaction
from .base import BaseService
from API.task import delete_photo
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)




class CreatePhotoService(BaseService):
    def process(self):
        user = self.data['user']
        validated_data = self.data['validated_data']
        if 'moderation' not in validated_data:
            validated_data['moderation'] = '2'
        photo = Photo.objects.create(author=user, **validated_data) # Сохраняем фото сюда, чтобы получить его ID
        
        # Notify user with subject
        self.notify_user(
            user,
            f"Фотография '{validated_data['title']}' Отправлена на модерацию.",
            'photo_created',
            photo_title = validated_data['title'],  # передаем title
            photo_id = photo.id,
            subject=f"Создание фотографии: {validated_data['title']}"  # Добавляем subject
        )

        return photo
