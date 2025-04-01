# API/task.py
from celery import shared_task
from galery.models import Photo
import os
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


@shared_task
def delete_photo(photo_id):
    try:
        photo = Photo.objects.get(pk=photo_id)
        
        # Проверяем актуальный статус фотографии
        if photo.moderation != '1' or not photo.deleted_at:
            print(f"Фото {photo_id} больше не помечено на удаление. Отмена задачи.")
            return
        
        # Проверяем, прошло ли 30 секунд с момента пометки на удаление
        if timezone.now() < photo.deleted_at + timedelta(seconds=30):
            print(f"Время удаления еще не наступило для фото {photo_id}")
            return

        # Удаляем файл и запись
        image_path = photo.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)
            print(f"Файл {image_path} удален")
            
        photo.delete()
        print(f"Фото {photo_id} удалено из БД")

    except Photo.DoesNotExist:
        print(f"Фото {photo_id} не найдено")
    except Exception as e:
        print(f"Ошибка при удалении фото {photo_id}: {str(e)}")