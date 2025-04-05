# API/task.py
from celery import shared_task
from galery.models import Photo
import os
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django.db import close_old_connections
from galery.models import Photo
import logging
from django.db import connection
logger = logging.getLogger(__name__)

from django.db import transaction

@shared_task(bind=True)
def delete_photo(self, photo_id):
    try:
        logger.info(f"Попытка удаления фото {photo_id}")
        
        with transaction.atomic():
            try:
                # Блокируем строку и проверяем, не восстановлено ли фото
                photo = Photo.objects.select_for_update().get(pk=photo_id)
                
                # Если фото восстановлено - отменяем удаление
                if photo.moderation != '1' or not photo.deleted_at:
                    logger.warning(f"Фото {photo_id} было восстановлено, удаление отменено")
                    return False
                    
                # Проверяем, прошло ли достаточно времени
                time_passed = (timezone.now() - photo.deleted_at).total_seconds()
                if time_passed < 30:
                    logger.info(f"Ждём ещё {30 - time_passed} секунд...")
                    raise self.retry(countdown=min(30 - time_passed, 10), max_retries=3)
                
                # Удаляем файл и запись
                if photo.image:
                    try:
                        file_path = os.path.join(settings.MEDIA_ROOT, str(photo.image))
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Ошибка удаления файла: {e}")
                
                photo.delete()
                logger.info(f"Фото {photo_id} успешно удалено")
                return True
                
            except Photo.DoesNotExist:
                logger.warning(f"Фото {photo_id} не найдено")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка при удалении фото {photo_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)