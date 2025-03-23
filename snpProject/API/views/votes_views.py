from rest_framework.response import Response
from rest_framework import status
from .photos_vews import BaseViewSet
from galery.models import Vote
from API.serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Votes"])
class VoteViewSet(BaseViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description="Create a vote for a photo.",
        request=VoteSerializer,
        responses={201: VoteSerializer, 400: {'description': 'Bad request'}},
    )
    def create(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            photo_id = request.data.get('photo')
            if not photo_id:
                return Response({'detail': 'photo ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            if Vote.objects.filter(author=request.user, photo_id=photo_id).exists():
                return Response(
                    {'detail': 'Вы уже поставили лайк этой фотографии.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            photo = Photo.objects.get(id=photo_id)  # Получаем объект фотографии
            vote = Vote.objects.create(author=request.user, photo=photo)
            serializer = self.get_serializer(vote)

            # Отправка уведомления автору фотографии
            if photo.author != request.user:  # Не отправляем уведомление себе
                message = f"Пользователь {request.user.username} поставил лайк вашей фотографии."
                self.notify_user(photo.author, message, 'like')

            return Response(serializer.data, status=status.HTTP_201_CREATED)