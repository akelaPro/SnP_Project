from datetime import timedelta
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from API.serializers import LoginSerializer, RefreshSerializer
from API.services import *
from API.authentication import CustomTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
from galery.models import UserToken
from API.utils import hash_token
import secrets
from rest_framework.permissions import AllowAny


from snpProject import settings



class LoginView(APIView):
    def post(self, request):
        # Валидация входных данных
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            # Выполнение бизнес-логики через сервис
            result = LoginService.execute({
                'email': serializer.validated_data['email'],
                'password': serializer.validated_data['password']
            })
            
            # Создаем ответ с куками
            response = Response(
                {
                    'status': 'success',
                    'user_id': result['user'].id,
                    'email': result['user'].email
                },
                status=status.HTTP_200_OK
            )
            
            # Устанавливаем куки
            response.set_cookie(
                'access_token',
                result['access_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=900,  # 15 минут
                path='/',
            )
            response.set_cookie(
                'refresh_token',
                result['refresh_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=604800,  # 7 дней
                path='/',
            )
            
            return response
            
        except exceptions.AuthenticationFailed as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'detail': 'Ошибка сервера при авторизации'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token missing'}, status=400)

        try:
            refresh_hash = hash_token(refresh_token)
            user_token = UserToken.objects.get(
                refresh_token_hash=refresh_hash,
                refresh_token_expires__gt=timezone.now()
            )
        except UserToken.DoesNotExist:
            return Response({'error': 'Invalid refresh token'}, status=401)

        # Generate new access token
        new_access_token = secrets.token_urlsafe(32)
        user_token.access_token_hash = hash_token(new_access_token)
        user_token.access_token_expires = timezone.now() + timedelta(minutes=15)
        user_token.save()

        response = Response({'status': 'token refreshed'})
        response.set_cookie(
            'access_token',
            new_access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=900
        )
        return response
class LogoutView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        LogoutService.execute({'user': request.user})
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

class VerifyTokenView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            auth = CustomTokenAuthentication()
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is None:
                return Response({
                    "status": "invalid",
                    "is_authenticated": False
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            user, _ = user_auth_tuple
            return Response({
                "status": "valid",
                "user_id": user.id,
                "email": user.email,
                "is_authenticated": True
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)