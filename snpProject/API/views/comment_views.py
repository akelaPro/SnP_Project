from .photos_vews import BaseViewSet
from galery.models import Comment
from API.serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        photo_id = self.request.query_params.get('photo')
        parent_id = self.request.query_params.get('parent') # Получаем параметр parent
        if photo_id:
            queryset = queryset.filter(photo_id=photo_id)
        if parent_id: # Если указан parent, фильтруем ответы только для этого родителя
            queryset = queryset.filter(parent_id=parent_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            parent=serializer.validated_data.get('parent')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['depth'] = 0  # Начальная глубина
        return context