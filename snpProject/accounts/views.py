from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.forms import UserRegistrationForm
from galery.serializers import PhotoSerializer
from .serializers import CreateSerializer, Serializer
from django.contrib.auth import get_user_model
from galery.models import Photo
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.views.decorators.csrf import csrf_exempt


class RegistrationTemplateView(TemplateView):
    template_name = 'accounts/registration.html'


class LoginTemplateView(TemplateView):
    template_name = 'accounts/login.html'


class UserProfileView(View):
    def get(self, request):
        return render(request, 'accounts/profile.html', {})


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
        serializer = PhotoSerializer(photos, many=True)
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
    

class RegisterView(APIView):
    def post(self, request):
        serializer = CreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomTokenObtainPairView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        return TokenObtainPairView.as_view()(request._request)