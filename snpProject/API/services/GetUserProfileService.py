from django.contrib.auth import get_user_model
from .base import BaseService
from API.serializers import Serializer

User = get_user_model()

class GetUserProfileService(BaseService):
    def process(self):
        user = self.data['user']
        serializer = Serializer(user)
        return serializer.data