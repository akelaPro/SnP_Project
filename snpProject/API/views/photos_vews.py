from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from API.task import delete_photo
from galery.models import Photo
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from API.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
import logging
from rest_framework.filters import SearchFilter, OrderingFilter


logger = logging.getLogger(__name__)

class BaseViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def notify_user(self, user, message, notification_type):
        notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )

class PhotoViewSet(BaseViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    parser_classes = [MultiPartParser, FormParser]
    # Добавляем OrderingFilter и настраиваем поиск
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['votes_count', 'published_at', 'comments_count']
    ordering = ['-published_at']  # Сортировка по умолчанию

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = Photo.objects.filter(
                Q(moderation='3') | Q(moderation='1', author=self.request.user)
                )
        else:
            queryset = Photo.objects.filter(moderation='3')

        # Аннотации для сортировки
        queryset = queryset.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )

        return queryset

    

    @action(detail=True, methods=['post'])
    def delete_photo(self, request, pk=None):
        photo = get_object_or_404(Photo, id=pk)
    
        if photo.author != request.user:
            return Response({'detail': 'У вас нет прав на удаление этой фотографии.'}, status=status.HTTP_403_FORBIDDEN)

        photo.moderation = '1'
        photo.deleted_at = timezone.now()
        photo.save()
    
    
        delete_photo.apply_async(args=(photo.id,), countdown=30)  
    
        serializer = self.get_serializer(photo)
        self.notify_user(request.user, f"Фотография '{photo.title}' помечена на удаление.", 'photo_deleted')
        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=True, methods=['post'])
    def restore_photo(self, request, pk=None):
        logger.info(f"restore_photo called with pk={pk}, user={request.user}")
        try:
        
            photo = self.get_object()  
            logger.info(f"Photo found: {photo.id}, moderation={photo.moderation}, deleted_at={photo.deleted_at}")

        
            if photo.author != request.user:
                logger.warning("Permission denied.")
                return Response({'detail': 'У вас нет прав на восстановление этой фотографии.'}, status=status.HTTP_403_FORBIDDEN)

        
            if photo.moderation != '1' or photo.deleted_at is None:
                logger.warning(f"Photo not marked for deletion. moderation={photo.moderation}, deleted_at={photo.deleted_at}")
                return Response({'detail': 'Фотография не помечена на удаление.'}, status=status.HTTP_400_BAD_REQUEST)

       
            if timezone.now() > photo.deleted_at + timezone.timedelta(seconds=60):
                logger.warning("Restore time expired.")
                return Response({'detail': 'Время для восстановления фотографии истекло.'}, status=status.HTTP_400_BAD_REQUEST)

       
            photo.moderation = '2'
            photo.deleted_at = None
            photo.save()
            serializer = self.get_serializer(photo)
            logger.info("Photo restored successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            return Response({'detail': 'Произошла ошибка при восстановлении фотографии.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)