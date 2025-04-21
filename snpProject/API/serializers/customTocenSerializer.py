# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Основное поле для входа
    password = serializers.CharField()

    def validate(self, data):
        # Используем EmailAuthBackend для аутентификации
        user = authenticate(
            request=self.context.get('request'),
            username=data['email'],
            password=data['password']
        )
        
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        
        data['user'] = user
        return data

class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()