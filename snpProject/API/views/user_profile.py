from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from serializers.photos import PhotoSerializer
from views.photos_vews import BaseViewSet
from galery.models.photo.models import Photo


class UserPhotosViewSet(BaseViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Photo.objects.filter(author=self.request.user)
        
        status_filter = self.request.query_params.get('moderation_status')
        if status_filter:
            queryset = queryset.filter(moderation=status_filter)
            
        return queryset.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-published_at')