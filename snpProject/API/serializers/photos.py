from rest_framework import serializers
from galery.models import Photo, Comment, Vote, User
from .auth import BaseUserSerializer

class PhotoSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    votes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    image = serializers.ImageField(required=True)  # Установите required=True
    has_liked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ['published_at', 'author', 'old_image']
        
         # added author
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

    def get_has_liked(self, obj): 
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return obj.votes.filter(author=user).exists()
        return False

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user  # Set the author here
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.moderation = validated_data.get('moderation', instance.moderation)
        instance.deleted_at = validated_data.get('deleted_at', instance.deleted_at)
        instance.save()
        return instance