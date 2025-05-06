from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from API.serializers import CommentSerializer
from API.services import *
from galery.models import *


@extend_schema(tags=["Comments"])
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'photo', 'parent')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        photo_id = self.request.query_params.get('photo')
        if photo_id:
            queryset = queryset.filter(photo_id=photo_id)
        return queryset

    def perform_create(self, serializer):
        comment = CreateCommentService.execute({
            'user': self.request.user,
            'validated_data': serializer.validated_data
        })
        serializer.instance = comment

    def destroy(self, request, *args, **kwargs):
        DeleteCommentService.execute({
            'comment': self.get_object(),
            'user': request.user
        })
        return Response(status=status.HTTP_204_NO_CONTENT)