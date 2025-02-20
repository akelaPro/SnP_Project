from .photos_vews import BaseViewSet
from galery.models import Comment
from API.serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Изменено на IsAuthenticated

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            super().perform_create(serializer)
            photo = serializer.instance.photo
            self.notify_user(photo.author, f"Новый комментарий на вашу фотографию '{photo.title}': {serializer.instance.text}", 'new_comment')

    def perform_update(self, serializer):
            super().perform_update(serializer)
            photo = serializer.instance.photo
            self.notify_user(photo.author, f"Изменен комментарий на вашу фотографию '{photo.title}': {serializer.instance.text}", 'comment_changed')

    def get_queryset(self):
        photo_id = self.request.query_params.get('photo')
        if photo_id:
            return self.queryset.filter(photo_id=photo_id)
        return self.queryset