from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from API.serializers.votes import VoteSerializer
from galery.models import Vote
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
import logging

from galery.models.photo.models import Photo

logger = logging.getLogger(__name__)

@extend_schema(tags=["Votes"])
class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

    def create(self, request, *args, **kwargs):
        photo_id = request.data.get('photo')
        if not photo_id:
            return Response(
                {'detail': 'Не указан photo ID в теле запроса.'},  # Конкретное сообщение
                status=status.HTTP_400_BAD_REQUEST
            )

        photo = get_object_or_404(Photo, pk=photo_id)

        # Проверяем существующий лайк и возвращаем его ID если есть
        existing_vote = Vote.objects.filter(author=request.user, photo=photo).first()
        if existing_vote:
            return Response(
                {
                    'detail': 'Лайк уже существует',
                    'vote_id': existing_vote.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        vote = Vote.objects.create(author=request.user, photo=photo)
        serializer = self.get_serializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        vote_id = kwargs.get('pk')  # Получаем vote_id из URL
        if not vote_id:
            return Response(
                {'detail': 'Не указан ID лайка в URL.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            vote = get_object_or_404(Vote, pk=vote_id, author=request.user)
            vote.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'detail': 'Лайк не найден или не принадлежит вам.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Ошибка при удалении лайка: {e}")
            return Response({'detail': f'Ошибка при удалении лайка: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)