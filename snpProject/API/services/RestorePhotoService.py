from galery.models import Photo
from django.utils import timezone
from django.db import transaction
from .base import BaseService
from API.task import delete_photo
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)



class RestorePhotoService(BaseService):
    def process(self):
        photo = self.data['photo']
        user = self.data['user']
        
        with transaction.atomic():
            photo = Photo.objects.select_for_update().get(pk=photo.id)
            
            if photo.author != user:
                raise exceptions.PermissionDenied("Нет прав на восстановление")
                
            if photo.moderation != '1':
                raise exceptions.ValidationError("Фото не помечено на удаление")

            photo.moderation = '3'
            photo.deleted_at = None
            photo.delete_task_id = None
            photo.save()
            
            try:
                self.notify_user(
                    photo.author,
                    f"Фотография '{photo.title}' востановленна.",
                    'photo_deleted',
                    subject=f"Восстановление фотографии: {photo.title}"
                )
            except Exception as e:
                logger.error(f"Notification failed but photo is still marked for redtore: {str(e)}")

        return photo
