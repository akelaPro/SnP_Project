from rest_framework import serializers
from galery.models import Photo, Comment
from .auth import BaseUserSerializer

from rest_framework import serializers
from galery.models import Photo, Comment
from .auth import BaseUserSerializer

#class RecursiveField(serializers.Serializer):
    #def to_representation(self, value):
       # serializer = CommentSerializer(value, context=self.context)
       # return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'author', 'photo', 'parent', 'replies']
        read_only_fields = ['id', 'created_at', 'replies', 'author']

    def get_replies(self, obj):
        depth = self.context.get('depth', 0)
        if depth < 2: # Максимальная глубина - 2
            serializer = CommentSerializer(obj.replies.all(), many=True, context={'depth': depth + 1, 'request': self.context.get('request')})
            return serializer.data
        return []