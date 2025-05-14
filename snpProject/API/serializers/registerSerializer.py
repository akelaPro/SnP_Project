from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
import secrets
from django.db.models import ObjectDoesNotExist

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'password2', 'avatar') # Добавили 'username'
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'password2': {'write_only': True, 'style': {'input_type': 'password'}},
            'username': {'read_only': True} # username генерируется автоматически
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        email = validated_data['email']
        password = validated_data['password']
        avatar = validated_data.get('avatar')

        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while True:
            try:
                get_user_model().objects.get(username=username)
                username = f"{base_username}_{counter}"
                counter += 1
            except ObjectDoesNotExist:
                break

        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
            avatar=avatar
        )
        return user