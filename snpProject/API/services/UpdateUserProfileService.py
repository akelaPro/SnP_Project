from django.contrib.auth import get_user_model
from .base import BaseService
from API.serializers import Serializer

User = get_user_model()

class UpdateUserProfileService(BaseService):
    def process(self):
        user = self.data['user']
        request_data = self.data['request_data']
        
        serializer = Serializer(user, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return serializer.data