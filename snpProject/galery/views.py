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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


def home(request): 
    return render(request, 'galery/index.html')  

def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'galery/photo.html', {'photo': photo})
  


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

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def restore_photo(request, pk):
        try:
            photo = Photo.objects.get(pk=pk, author=request.user, moderation='1')  # Assuming '1' is the status for 'deleted'
        except Photo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        photo.restore()

        return Response(status=status.HTTP_200_OK)

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
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def get_queryset(self):
        photo_id = self.request.query_params.get('photo')
        if photo_id:
            return self.queryset.filter(photo_id=photo_id)
        return self.queryset

class VoteViewSet(BaseViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        photo_id = request.data.get('photo')
        if not photo_id:
            return Response({'detail': 'photo ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Vote.objects.filter(author=request.user, photo_id=photo_id).exists():
            return Response(
            {'detail': 'Вы уже поставили лайк этой фотографии.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
        return super().create(request, *args, **kwargs)



    def destroy(self, request, *args, **kwargs):
        vote = self.get_object()
        if vote.author != request.user:
            return Response(
                {'detail': 'Вы можете удалять только свои лайки.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
