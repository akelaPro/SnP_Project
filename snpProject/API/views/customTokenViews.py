from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.contrib.auth import authenticate
from django.utils import timezone
from API.authentication import CustomTokenAuthentication
from API.serializers import *
from galery.models import *
from API.utils import hash_token
import secrets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema



@extend_schema(
    tags=["Auth"],
    description="Авторизация пользователя.",
    request=LoginSerializer,
    responses={200: LoginSerializer, 400: 'Bad Request'},
)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            raise exceptions.AuthenticationFailed('Invalid credentials.')

        # Генерация токенов
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        # Сохранение токенов
        UserToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token_hash': hash_token(access_token),
                'refresh_token_hash': hash_token(refresh_token),
                'access_token_expires': timezone.now() + timezone.timedelta(minutes=2), #2 минуты
                'refresh_token_expires': timezone.now() + timezone.timedelta(days=7),
            }
        )

        return Response({
            'access': access_token,
            'refresh': refresh_token,
        })


@extend_schema(
    tags=["Auth"],
    description="Обновление токена (если необходимо)",
    responses={200: RefreshSerializer, 400: 'Bad Request'},
)
class RefreshView(APIView):
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']

        refresh_hash = hash_token(refresh_token)
        try:
            user_token = UserToken.objects.get(refresh_token_hash=refresh_hash)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid refresh token.')

        if timezone.now() > user_token.refresh_token_expires:
            raise exceptions.AuthenticationFailed('Refresh token expired.')

        # Генерация новых токенов
        new_access = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)

        user_token.access_token_hash = hash_token(new_access)
        user_token.refresh_token_hash = hash_token(new_refresh)
        user_token.access_token_expires = timezone.now() + timezone.timedelta(minutes=2) #2 минуты
        user_token.refresh_token_expires = timezone.now() + timezone.timedelta(days=7)
        user_token.save()

        return Response({
            'access': new_access,
            'refresh': new_refresh,
        })


@extend_schema(
    tags=["Auth"],
    description="Выход пользователя",
    responses={204: 'No Content'},
)
class LogoutView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.token.delete()
        except:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    description="Проверяет, действителен ли токен пользователя.",
    responses={200: {'description': 'Token is valid'}},  # Укажите описание ответа
)
class VerifyTokenView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"status": "valid"}, status=status.HTTP_200_OK)