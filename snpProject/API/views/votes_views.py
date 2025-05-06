from rest_framework.response import Response
from rest_framework import status

from API.services import *
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

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Требуется авторизация'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            vote = CreateVoteService.execute({
                'user': request.user,
                'photo_id': request.data.get('photo')
            })
            serializer = self.get_serializer(vote)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except exceptions.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': 'Произошла ошибка при обработке запроса'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )