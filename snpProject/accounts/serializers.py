from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

class CreateSerializer(UserCreateSerializer): 
    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password', 'avatar')

class Serializer(UserSerializer):  
    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'username', 'email', 'avatar')
