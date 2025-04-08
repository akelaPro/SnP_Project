from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from API.services.user import GetUserProfileService, UpdateUserProfileService

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = GetUserProfileService.execute({'user': request.user})
        return Response(data)

class UpdateUserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = UpdateUserProfileService.execute({
            'user': request.user,
            'request_data': request.data
        })
        return Response(data)