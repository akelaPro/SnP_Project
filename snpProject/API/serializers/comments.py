from rest_framework import serializers
from galery.models import Photo, Comment
from .auth import BaseUserSerializer
from django.core.exceptions import PermissionDenied

class CommentSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'author', 'photo', 'parent', 'replies', 'can_delete']
        read_only_fields = ['id', 'created_at', 'replies', 'author']

    def get_replies(self, obj):
        depth = self.context.get('depth', 0)
        if depth < 2:  # Ограничение глубины вложенности
            serializer = CommentSerializer(obj.replies.all(), many=True, context={'depth': depth + 1, 'request': self.context.get('request')})
            return serializer.data
        return []
    
    def get_can_delete(self, obj):
        user = self.context['request'].user
        return obj.author == user and obj.can_delete()


    def validate(self, attrs):
        if 'parent' in attrs and attrs['parent']:
            if attrs['parent'].photo != attrs['photo']:
                raise serializers.ValidationError({"parent": "Ответ должен быть к тому же фото."})
        return attrs