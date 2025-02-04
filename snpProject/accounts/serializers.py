from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



# accounts/serializers.py
class CreateSerializer(UserCreateSerializer): 
    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password', 'avatar')
        extra_kwargs = {
            'username': {'required': False} 
        }

    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0]
        return super().create(validated_data)

class Serializer(UserSerializer):  
    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'avatar')






class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email' 

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  
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