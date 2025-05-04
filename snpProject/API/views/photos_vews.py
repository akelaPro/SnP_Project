from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from API.serializers import PhotoSerializer
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter  # Импортируем классы фильтров
from API.services.list import PhotoListService
from galery.models import Photo
from API.serializers import PhotoSerializer
from galery.models import *
from API.services import *


@extend_schema(tags=["Photos"])
class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.none()  # Будет переопределено в get_queryset
    serializer_class = PhotoSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [SearchFilter, OrderingFilter]  # Используем классы фильтров напрямую
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['votes_count', 'published_at', 'comments_count']
    ordering = ['-published_at']

    def get_queryset(self):
        # Получаем параметр include_deleted из запроса
        include_deleted = self.request.query_params.get('include_deleted', 'false').lower() == 'true'
        
        # Получаем базовый queryset из сервиса
        base_queryset = PhotoListService().execute({
            'action': self.action,
            'include_deleted': include_deleted  # Передаем параметр в сервис
        })

        # Применяем стандартные DRF фильтры (поиск и сортировка)
        for backend_class in self.filter_backends:
            base_queryset = backend_class().filter_queryset(self.request, base_queryset, self)

        return base_queryset


    def perform_create(self, serializer):
        photo = CreatePhotoService().execute({
            'user': self.request.user,
            'validated_data': serializer.validated_data
        })
        serializer.instance = photo

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        photo = self.get_object()
        # Блокируем запись на время операции
        locked_photo = Photo.objects.select_for_update().get(pk=photo.id)
        DeletePhotoService().execute({
            'photo': locked_photo,
            'user': request.user
        })
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore_photo(self, request, pk=None):
        photo = RestorePhotoService.execute({
            'photo': self.get_object(),
            'user': request.user
        })
        serializer = self.get_serializer(photo)
        return Response(serializer.data)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        photo = UpdatePhotoService().execute({
            'photo': instance,
            'user': request.user,
            'serializer_class': self.get_serializer_class(),
            'request': request
        })

        serializer = self.get_serializer(photo)
        return Response(serializer.data)