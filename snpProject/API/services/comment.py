from galery.models import Comment
from .base import BaseService
from rest_framework import exceptions

class CreateCommentService(BaseService):
    def process(self):
        user = self.data['user']
        validated_data = self.data['validated_data']
        
        comment = Comment.objects.create(author=user, **validated_data)

        # Уведомления
        if comment.photo.author != user:
            self.notify_user(
                comment.photo.author,
                f"Пользователь {user.username} оставил комментарий к вашей фотографии.",
                'comment'
            )

        if comment.parent and comment.parent.author != user:
            self.notify_user(
                comment.parent.author,
                f"Пользователь {user.username} ответил на ваш комментарий.",
                'reply'
            )

        return comment

class DeleteCommentService(BaseService):
    def process(self):
        comment = self.data['comment']
        user = self.data['user']
        
        if comment.author != user:
            raise exceptions.PermissionDenied("Вы не можете удалить чужой комментарий.")
        
        if not comment.can_delete():
            raise exceptions.ValidationError("Нельзя удалить комментарий с ответами.")
            
        comment.delete()