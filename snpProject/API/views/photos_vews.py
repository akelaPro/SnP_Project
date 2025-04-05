from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from API.serializers import PhotoSerializer
from rest_framework.decorators import action
from django.db import transaction
from galery.models import *
from API.services.photo import (
    CreatePhotoService, 
    DeletePhotoService,
    RestorePhotoService,
    UpdatePhotoService
)



@extend_schema(tags=["Photos"])
class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def perform_create(self, serializer):
        photo = CreatePhotoService.execute({
            'user': self.request.user,
            'validated_data': serializer.validated_data
        })
        serializer.instance = photo

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        photo = self.get_object()
        # Блокируем запись на время операции
        locked_photo = Photo.objects.select_for_update().get(pk=photo.id)
        DeletePhotoService.execute({
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

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        photo = UpdatePhotoService.execute({
            'photo': self.get_object(),
            'user': request.user,
            'validated_data': serializer.validated_data
        })
        
        serializer = self.get_serializer(photo)
        return Response(serializer.data)