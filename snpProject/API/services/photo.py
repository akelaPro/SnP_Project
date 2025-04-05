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
        return Photo.objects.create(author=user, **validated_data)

class DeletePhotoService(BaseService):
    def process(self):
        photo = self.data['photo']
        user = self.data['user']
        
        if photo.author != user:
            raise exceptions.PermissionDenied("Нет прав на удаление")

        logger.info(f"Marking photo {photo.id} for deletion")

        with transaction.atomic():
            updated = Photo.objects.filter(pk=photo.id).update(
                moderation='1',
                deleted_at=timezone.now()
            )
            if not updated:
                raise exceptions.ValidationError("Failed to mark photo for deletion")
            
            photo.refresh_from_db()

        logger.info(f"Photo marked - moderation: {photo.moderation}, deleted_at: {photo.deleted_at}")

        # Verify the photo is properly marked before creating task
        if photo.moderation != '1' or not photo.deleted_at:
            raise exceptions.ValidationError("Failed to properly mark photo for deletion")

        task = delete_photo.apply_async(args=(photo.id,), countdown=60)
        
        with transaction.atomic():
            Photo.objects.filter(pk=photo.id).update(delete_task_id=task.id)
            photo.refresh_from_db()

        logger.info(f"Delete task created: {task.id}")

        # Notify user with subject
        self.notify_user(
            photo.author,
            f"Фотография '{photo.title}' помечена на удаление.",
            'photo_deleted',
            subject=f"Удаление фотографии: {photo.title}"  # Добавляем subject
        )

        return photo


class RestorePhotoService(BaseService):
    def process(self):
        photo = self.data['photo']
        user = self.data['user']
        
        logger.info(f"Попытка восстановления фото {photo.id}. Текущий статус: moderation={photo.moderation}, deleted_at={photo.deleted_at}")
        
        if photo.author != user:
            raise exceptions.PermissionDenied("Нет прав на восстановление")
            
        if photo.moderation != '1':
            logger.warning(f"Фото {photo.id} не помечено на удаление (moderation={photo.moderation})")
            raise exceptions.ValidationError("Фото не помечено на удаление")

        if photo.delete_task_id:
            from celery.result import AsyncResult
            task = AsyncResult(photo.delete_task_id)
            if not task.ready():
                logger.info(f"Отменяем задачу удаления {photo.delete_task_id}")
                task.revoke()

        photo.moderation = '3'
        photo.deleted_at = None
        photo.delete_task_id = None
        photo.save()
        
        logger.info(f"Фото {photo.id} успешно восстановлено")

class UpdatePhotoService(BaseService):
    def process(self):
        photo = self.data['photo']
        user = self.data['user']
        validated_data = self.data['validated_data']
        
        if photo.author != user:
            raise exceptions.PermissionDenied("Вы не можете изменять эту фотографию.")
            
        for attr, value in validated_data.items():
            setattr(photo, attr, value)
        photo.save()
        
        self.notify_user(
            photo.author,
            f"Фотография '{photo.title}' успешно обновлена.",
            'photo_updated'
        )
        
        return photo