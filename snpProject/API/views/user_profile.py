from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from API.serializers import *
from galery.models.photo.models import Photo
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(tags=["User Photos"])
class UserLisPhoto(ListAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['votes_count', 'published_at', 'comments_count', 'moderation']
    ordering = ['-published_at']
    queryset = Photo.objects.all()



    @extend_schema(
        description="Get photos for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name='moderation_status',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by moderation status',
                required=False,
            ),
        ],
        responses={200: PhotoSerializer(many=True)}
    )
    def get_queryset(self):
        queryset = Photo.objects.filter(author=self.request.user)
        status = self.request.query_params.get('moderation_status')
        if status:
            queryset = queryset.filter(moderation=status)
            
        return queryset.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-published_at')