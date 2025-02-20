from rest_framework import serializers
from API.serializers.auth import BaseUserSerializer
from galery.models import Photo, Comment, Vote, User

class PhotoSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    votes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    image = serializers.ImageField()
    has_liked = serializers.SerializerMethodField()


    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ['published_at', 'deleted_at', 'moderation']

    def get_has_liked(self, obj): 
        request = self.context.get('request')
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.votes.filter(author=user).exists()
        return False