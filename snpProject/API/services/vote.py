from rest_framework import exceptions

from galery.models import Vote, Photo
from .base import BaseService

class CreateVoteService(BaseService):
    def process(self):
        user = self.data['user']
        photo_id = self.data['photo_id']
        
        if not photo_id:
            raise exceptions.ValidationError('photo ID is required.')
            
        if Vote.objects.filter(author=user, photo_id=photo_id).exists():
            raise exceptions.ValidationError('Вы уже поставили лайк этой фотографии.')

        photo = Photo.objects.get(id=photo_id)
        vote = Vote.objects.create(author=user, photo=photo)
        photo.save()
        # Отправка уведомления автору фотографии
        if photo.author != user:
            message = f"Пользователь {user.username} поставил лайк вашей фотографии."
            self.notify_user(photo.author, message, 'like')

        return vote