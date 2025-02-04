from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)  # Get a logger instance

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                logger.info(f"Authentication successful for user: {username}")  # Log successful authentication
                return user
            else:
                logger.warning(f"Incorrect password for user: {username}")  # Log incorrect password attempt
        except UserModel.DoesNotExist:
            logger.warning(f"User with email {username} does not exist")  # Log user not found
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")  # Log user not found
            return None