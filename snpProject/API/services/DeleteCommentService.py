from galery.models import Comment
from .base import BaseService
from rest_framework import exceptions


class DeleteCommentService(BaseService):
    def process(self):
        comment = self.data['comment']
        user = self.data['user']
        
        if comment.author != user:
            raise exceptions.PermissionDenied("Вы не можете удалить чужой комментарий.")
        
        if not comment.can_delete():
            raise exceptions.ValidationError("Нельзя удалить комментарий с ответами.")
            
        comment.delete()