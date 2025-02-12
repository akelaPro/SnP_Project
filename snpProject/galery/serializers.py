from rest_framework import serializers
from galery.models import Photo, Comment, Vote, User
from snpProject import settings

class BaseUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    avatar_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'avatar_thumbnail']

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return self.context['request'].build_absolute_uri(settings.DEFAULT_USER_IMAGE)


    def get_avatar_thumbnail(self, obj):
        if obj.avatar_thumbnail:
            return self.context['request'].build_absolute_uri(obj.avatar_thumbnail.url)
        return self.context['request'].build_absolute_uri(settings.DEFAULT_USER_IMAGE)


class UserSerializer(BaseUserSerializer):
    pass  

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

class VoteSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())

    class Meta:
        model = Vote
        fields = '__all__'
        read_only_fields = []

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
