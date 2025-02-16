from rest_framework import serializers
from galery.models import Photo, Comment, Vote, User
from .auth import BaseUserSerializer

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
