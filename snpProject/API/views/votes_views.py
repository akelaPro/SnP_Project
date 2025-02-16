from rest_framework.response import Response
from rest_framework import status
from .photos_vews import BaseViewSet
from galery.models import Vote
from API.serializers import *
from rest_framework.permissions import IsAuthenticated


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
