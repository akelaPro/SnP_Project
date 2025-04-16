# API/task.py
from celery import shared_task
from galery.models import Photo
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
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from decouple import config

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60, max_retries=3)
def delete_photo(self, photo_id):
    try:
        logger.info(f"Attempting to delete photo {photo_id}")
        
        with transaction.atomic():
            # Lock the photo row
            photo = Photo.objects.select_for_update().get(pk=photo_id)
            
            # Check if still marked for deletion
            if photo.moderation != '1' or not photo.deleted_at:
                logger.warning(f"Photo {photo_id} was restored, deletion cancelled")
                return False
                
            # Check if enough time has passed
            time_passed = (timezone.now() - photo.deleted_at).total_seconds()
            if time_passed < 30:
                logger.info(f"Waiting {30 - time_passed} more seconds...")
                raise self.retry(countdown=min(30 - time_passed, 10))
            
            # Delete file from Yandex Object Storage
            if photo.image:
                try:
                    storage = S3Boto3Storage()
                    file_name = photo.image.name  # Получаем имя файла относительно бакета
                    storage.delete(file_name) # Удаляем файл из бакета
                    logger.info(f"Deleted file {file_name} for photo {photo_id} from Yandex Object Storage")
                except Exception as e:
                    logger.error(f"Error deleting file from Yandex Object Storage: {str(e)}")
                    # Don't fail the task just because file deletion failed
            
            # Delete record
            photo.delete()
            logger.info(f"Photo {photo_id} successfully deleted")
            return True
            
    except Photo.DoesNotExist:
        logger.warning(f"Photo {photo_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error deleting photo {photo_id}: {str(e)}")
        raise self.retry(exc=e)