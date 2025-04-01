from rest_framework import exceptions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from galery.models import Comment
from API.serializers import CommentSerializer
from .photos_vews import BaseViewSet  # Assuming this is defined elsewhere

@extend_schema(tags=["Comments"])
class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        photo_id = self.request.query_params.get('photo')
        parent_id = self.request.query_params.get('parent')
        if photo_id:
            queryset = queryset.filter(photo_id=photo_id)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        # Отправка уведомления автору фотографии
        if comment.photo.author != self.request.user:  # Не отправляем уведомление себе
            message = f"Пользователь {self.request.user.username} оставил комментарий к вашей фотографии."
            self.notify_user(comment.photo.author, message, 'comment')

        # Отправка уведомления автору родительского комментария, если это ответ
        if comment.parent and comment.parent.author != self.request.user:  # Не отправляем уведомление себе
            message = f"Пользователь {self.request.user.username} ответил на ваш комментарий."
            self.notify_user(comment.parent.author, message, 'reply')  # Убрал parent тут, чтобы обрабатывать в сериализаторе

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise exceptions.PermissionDenied("Вы не можете удалить чужой комментарий.")
        if not instance.can_delete():
            return Response({"detail": "Нельзя удалить комментарий с ответами."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['depth'] = 0
        return context