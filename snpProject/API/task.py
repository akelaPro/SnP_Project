# API/task.py
from celery import shared_task
from galery.models import Photo
import os
from django.conf import settings

@shared_task
def delete_photo(photo_id):
    """
    Фактически удаляет фотографию из базы данных и файловой системы.
    """
    try:
        photo = Photo.objects.get(pk=photo_id)  


        if photo.moderation == '1':
            image_path = photo.image.path
            photo.delete()


            if os.path.isfile(image_path):
                os.remove(image_path)
                print(f"Фотография '{image_path}' успешно удалена из файловой системы.")
            else:
                print(f"Файл '{image_path}' не найден.")
        else:
            print(f"Фотография с id {photo_id} больше не помечена на удаление.")

    except Photo.DoesNotExist:
        print(f"Фотография с id {photo_id} не найдена.")
    except Exception as e:
        print(f"Ошибка при удалении фотографии {photo_id}: {e}")