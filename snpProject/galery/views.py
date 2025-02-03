from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from galery.models import Photo, Comment, Vote
from galery.serializers import CommentSerializer, PhotoSerializer, VoteSerializer
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.db.models import Count, Q



def home(request): 
    return render(request, 'galery/index.html')  

def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'galery/photo_detail.html', {'photo': photo})
  


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
    queryset = Photo.objects.filter(moderation='3')
    serializer_class = PhotoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) | 
                Q(author__username__icontains=search_query)
            )
        sort_option = self.request.query_params.get('sort', '')
        if sort_option == 'votes':
            queryset = queryset.annotate(vote_count=Count('votes')).order_by('-vote_count')
        elif sort_option == 'date':
            queryset = queryset.order_by('-published_at')
        elif sort_option == 'comments':
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count')
        return queryset

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.moderation = '1'
            instance.deleted_at = timezone.now()
            instance.save
        self.notify_user(instance.author, f"Ваша фотография '{instance.title}' помечена на удаление.", 'photo_deleted')

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        self.notify_user(serializer.instance.author, f"Ваша фотография '{serializer.instance.title}' изменена.", 'photo_changed')

class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        photo = serializer.instance.photo
        self.notify_user(photo.author, f"Новый комментарий на вашу фотографию '{photo.title}': {serializer.instance.text}", 'new_comment')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        photo = serializer.instance.photo
        self.notify_user(photo.author, f"Изменен комментарий на вашу фотографию '{photo.title}': {serializer.instance.text}", 'comment_changed')

class VoteViewSet(BaseViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    lookup_field = 'pk'

    def perform_create(self, serializer):
        super().perform_create(serializer)
        photo = serializer.instance.photo
        self.notify_user(photo.author, f"Ваша фотография '{photo.title}' получила новый лайк!", 'new_like')

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            photo = instance.photo
            super().perform_destroy(instance)
            self.notify_user(photo.author, f"Ваша фотография '{photo.title}' лайк был убран!", 'delete_like')

