from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from API.task import delete_photo
from galery.models import Photo
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.db.models import Count, Q
from API.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
import logging
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied



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

@extend_schema(tags=["Photos"])
class PhotoViewSet(BaseViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['votes_count', 'published_at', 'comments_count']
    ordering = ['-published_at']

    def get_queryset(self):
        queryset = Photo.objects.filter(moderation='3')  # Только одобренные фотографии

    # Аннотации для подсчета лайков и комментариев
        queryset = queryset.annotate(
        votes_count=Count('votes', distinct=True),
        comments_count=Count('comments', distinct=True)
        )
        if self.request.query_params.get('include_deleted') == 'true':
            queryset = Photo.objects.all()

        return queryset


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.author != request.user:
            raise PermissionDenied("Нет прав на удаление")
        
        # Помечаем на удаление
        instance.moderation = '1'
        instance.deleted_at = timezone.now()
        instance.save()
        
        # Сохраняем ID задачи для возможной отмены
        task = delete_photo.apply_async(args=(instance.id,), countdown=30)
        instance.delete_task_id = task.id
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Restore a deleted photo.",
        responses={200: PhotoSerializer, 400: {'description': 'Invalid request'}, 403: {'description': 'Permission denied'}},
    )
    @action(detail=True, methods=['post'])
    def restore_photo(self, request, pk=None):
        try:
            print(f"Начало восстановления фото {pk}")  # Лог
            photo = self.get_object()
            print(f"Фото {pk} получено")  # Лог

            if photo.author != request.user:
                print(f"Нет прав на восстановление фото {pk}")  # Лог
                return Response({"detail": "Нет прав"}, status=403)

            if photo.moderation != '1':
                print(f"Фото {pk} не помечено на удаление")  # Лог
                return Response({"detail": "Фото не помечено на удаление"}, status=400)

        # Отменяем задачу удаления
            from celery.result import AsyncResult
            if photo.delete_task_id:
                print(f"Попытка отмены задачи {photo.delete_task_id} для фото {pk}")  # Лог
                AsyncResult(photo.delete_task_id).revoke()
                print(f"Задача {photo.delete_task_id} отменена для фото {pk}")  # Лог

        # Восстанавливаем фото
            print(f"Восстановление фото {pk}")  # Лог
            photo.moderation = '3'
            photo.deleted_at = None
            photo.delete_task_id = None
            photo.save()
            print(f"Фото {pk} сохранено")  # Лог

            print(f"Отправка ответа для фото {pk}")  # Лог
            serializer = PhotoSerializer(photo, context={'request': request})
            return Response(serializer.data)

        except Exception as e:
            logger.exception(f"Ошибка при восстановлении фото {pk}: {e}")  # Лог с исключением
            return Response({"detail": str(e)}, status=500)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
    
    # Проверяем, что текущий пользователь является автором фотографии
        if instance.author != request.user:
            raise PermissionDenied("Вы не можете изменять эту фотографию.")
    
    # Проверяем, был ли изменён файл фотографии
        if 'image' in request.FILES:
            new_image = request.FILES['image']
            instance.old_image = instance.image  # Сохраняем старую версию фото
            instance.image = new_image
            instance.moderation = '2'  # Отправляем на модерацию
            instance.save()
            print(f"Файл сохранен: {instance.image.path}")  # Логируем путь к файлу
    
    # Обновляем остальные поля (название и описание)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
    
        return Response(serializer.data)