from rest_framework import generics, permissions
from API.serializers import RegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

class RegistrationAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Разрешить любому пользователю регистрироваться

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)