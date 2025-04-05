from rest_framework.response import Response
from rest_framework import status

from API.services.vote import CreateVoteService
from galery.models import Vote
from API.serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets


@extend_schema(tags=["Votes"])
class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description="Create a vote for a photo.",
        request=VoteSerializer,
        responses={201: VoteSerializer, 400: {'description': 'Bad request'}},
    )
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            vote = CreateVoteService.execute({
                'user': request.user,
                'photo_id': request.data.get('photo')
            })
            serializer = self.get_serializer(vote)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)