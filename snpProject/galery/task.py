# galery/tasks.py
from celery import shared_task
from .models import Photo
import os
@shared_task
def delete_photo(photo_id):
    try:
        photo = Photo.objects.get(id=photo_id)

        file_path = photo.image.path
        

        photo.delete()


        if os.path.isfile(file_path):
            os.remove(file_path)
    except Photo.DoesNotExist:
        pass
