from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class CreateSerializer(UserCreateSerializer): 
    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password', 'avatar')

class Serializer(UserSerializer):  
    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'avatar')






class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Укажите, что email - это поле для логина

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Используйте email для аутентификации
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    "Неверные учетные данные."
                )

        else:
            raise serializers.ValidationError(
                "Необходимо указать email и пароль."
            )

        data = super().validate(attrs)
        return data