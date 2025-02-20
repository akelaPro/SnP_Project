from rest_framework import serializers
from API.serializers.auth import BaseUserSerializer
from galery.models import Photo, Comment, Vote, User

class CommentSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)