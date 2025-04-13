from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from API.serializers import LoginSerializer, RefreshSerializer
from API.services import *
from API.authentication import CustomTokenAuthentication
from rest_framework.permissions import IsAuthenticated

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tokens = LoginService.execute({
            'username': serializer.validated_data['username'],
            'password': serializer.validated_data['password']
        })
        return Response(tokens)

class RefreshView(APIView):
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tokens = RefreshService.execute({
            'refresh_token': serializer.validated_data['refresh']
        })
        return Response(tokens)

class LogoutView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        LogoutService.execute({'user': request.user})
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class VerifyTokenView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"status": "valid"}, status=status.HTTP_200_OK)