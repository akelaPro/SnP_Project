from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from API.services.base import BaseService
from API.services.base import BaseService
from API.utils import hash_token


User = get_user_model()

class PasswordResetConfirmService(BaseService):
    def process(self):
        email = self.data.get('email')
        token = self.data.get('token')
        new_password = self.data.get('new_password')
        
        try:
            user = User.objects.get(email=email)
            
            # Проверяем токен и срок его действия
            token_hash = hash_token(token)
            if (user.password_reset_token_hash != token_hash or 
                user.password_reset_token_expires < timezone.now()):
                raise exceptions.ValidationError('Недействительная или просроченная ссылка для сброса пароля')
            
            # Устанавливаем новый пароль
            user.set_password(new_password)
            
            # Очищаем токен сброса
            user.password_reset_token_hash = None
            user.password_reset_token_expires = None
            user.save()
            
            # Отправляем уведомление об успешном сбросе пароля
            self.notify_user(
                user=user,
                message='Ваш пароль был успешно изменен.',
                notification_type='password_reset_success',
                subject='Пароль изменен'
            )
            
            return {'status': 'success'}
            
        except ObjectDoesNotExist:
            raise exceptions.ValidationError('Пользователь не найден')