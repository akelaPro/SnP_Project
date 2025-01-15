# galery/tasks.py
from celery import shared_task
from .models import Photo

@shared_task
def delete_photo(photo_id):
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.delete()  # Удаляем фотографию из базы данных
    except Photo.DoesNotExist:
        pass
