from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from API.serializers import *
from django.contrib.auth import get_user_model
from galery.models import Photo
from rest_framework.generics import CreateAPIView




class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = Serializer(user)
        return Response(serializer.data)

class UserPhotosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        photos = Photo.objects.filter(author=request.user)
        serializer = PhotoSerializer(photos, many=True, context={'request': request})  
        return Response(serializer.data)


class UpdateUserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = Serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    

class CreateUser(CreateAPIView):
    serializer_class = CreateSerializer