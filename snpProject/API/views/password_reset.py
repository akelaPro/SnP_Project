from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from API.serializers.password_reset import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

from API.services import *



class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = PasswordResetRequestService.execute({
            'email': serializer.validated_data['email']
        })
        
        return Response(result, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = PasswordResetConfirmService.execute({
            'email': serializer.validated_data['email'],
            'token': serializer.validated_data['token'],
            'new_password': serializer.validated_data['new_password']
        })
        
        return Response(result, status=status.HTTP_200_OK)