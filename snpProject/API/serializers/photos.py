from rest_framework import serializers
from django.core.files.images import get_image_dimensions
from PIL import Image
import logging
from API.serializers.auth import BaseUserSerializer
from galery.models.photo.models import Photo

logger = logging.getLogger('api')

class PhotoSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    votes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    image = serializers.ImageField(required=False)
    has_liked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    votes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    status_display = serializers.SerializerMethodField()
    old_image = serializers.ImageField(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'description', 'author', 'image', 
            'published_at', 'status_display', 'deleted_at', 'comments',
            'votes', 'has_liked', 'can_edit', 'votes_count', 'old_image', 'delete_task_id', 'comments_count'
        ]
        read_only_fields = ['published_at', 'author', 'old_image']


    def get_status_display(self, obj):
        return obj.get_moderation_display()

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


    def validate_image(self, value):
        try:
        # Проверка изображения
            if value.size > 10 * 1024 * 1024:  # 10 MB
                raise serializers.ValidationError("Размер файла не должен превышать 10 МБ.")
            return value
        except Exception as e:
            logger.error(f"Ошибка при валидации изображения: {e}", exc_info=True)
        raise serializers.ValidationError("Некорректный файл изображения.")

    def update(self, instance, validated_data):
        if 'image' in validated_data:
            # Сохраняем текущее изображение как старое
            instance.old_image = instance.image
            instance.image = validated_data['image']
            instance.moderation = '2'  # Отправляем на модерацию

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance