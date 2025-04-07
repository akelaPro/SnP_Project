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
        photo = Photo.objects.create(author=user, **validated_data) # Сохраняем фото сюда, чтобы получить его ID
        
        # Notify user with subject
        self.notify_user(
            user,
            f"Фотография '{validated_data['title']}' успешно создана.",
            'photo_created',
            photo_title = validated_data['title'],  # передаем title
            photo_id = photo.id,
            subject=f"Удаление фотографии: {validated_data['title']}"  # Добавляем subject
        )

        return photo


class DeletePhotoService(BaseService):
    def process(self):
        photo = self.data['photo']
        user = self.data['user']
        
        if photo.author != user:
            raise exceptions.PermissionDenied("Нет прав на удаление")

        logger.info(f"Marking photo {photo.id} for deletion")

        # Single atomic transaction for all operations
        with transaction.atomic():
            # Lock the photo row for the entire operation
            locked_photo = Photo.objects.select_for_update().get(pk=photo.id)
            
            # Check if photo was already modified
            if locked_photo.moderation == '1' and locked_photo.deleted_at:
                logger.info(f"Photo {photo.id} is already marked for deletion")
                return locked_photo

            # Update photo status
            locked_photo.moderation = '1'
            locked_photo.deleted_at = timezone.now()
            locked_photo.save()

            # Create delete task
            task = delete_photo.apply_async(args=(locked_photo.id,), countdown=60)
            locked_photo.delete_task_id = task.id
            locked_photo.save()

            # Send notification inside the same transaction
            try:
                self.notify_user(
                    locked_photo.author,
                    f"Фотография '{locked_photo.title}' помечена на удаление.",
                    'photo_deleted',
                    subject=f"Удаление фотографии: {locked_photo.title}"
                )
            except Exception as e:
                logger.error(f"Notification failed but photo is still marked for deletion: {str(e)}")

            logger.info(f"Photo {locked_photo.id} marked for deletion, moderation: {locked_photo.moderation}")
            return locked_photo
        
        
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