from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'password2', 'avatar')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'password2': {'write_only': True, 'style': {'input_type': 'password'}},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            avatar=validated_data.get('avatar'),
            username=validated_data['email'].split('@')[0]  # Автоматический username
        )
        return user