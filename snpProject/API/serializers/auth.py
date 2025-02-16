from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers


from snpProject import settings


class CreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'email', 'password', 'avatar')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        validated_data.setdefault('username', validated_data['email'].split('@')[0])
        return super().create(validated_data)


class Serializer(UserSerializer):  
    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'avatar')


class BaseUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    avatar_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'avatar', 'avatar_thumbnail']

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return self.context['request'].build_absolute_uri(settings.DEFAULT_USER_IMAGE)


    def get_avatar_thumbnail(self, obj):
        if obj.avatar_thumbnail:
            return self.context['request'].build_absolute_uri(obj.avatar_thumbnail.url)
        return self.context['request'].build_absolute_uri(settings.DEFAULT_USER_IMAGE)