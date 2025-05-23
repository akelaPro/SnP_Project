from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from service_objects.services import Service
import secrets

from API.services.base import BaseService
from API.utils import hash_token
from notification.models import Notification

User = get_user_model()

class PasswordResetRequestService(BaseService):
    def process(self):
        email = self.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Генерируем токен сброса
            reset_token = secrets.token_urlsafe(32)
            reset_token_hash = hash_token(reset_token)
            
            # Устанавливаем срок действия токена (например, 1 час)
            reset_token_expires = timezone.now() + timedelta(hours=1)
            
            # Сохраняем токен в пользователе
            user.password_reset_token_hash = reset_token_hash
            user.password_reset_token_expires = reset_token_expires
            user.save()
            
            # Отправляем письмо с ссылкой для сброса
            reset_link = f"{settings.FRONTEND_URL}/password-reset/confirm?token={reset_token}&email={user.email}"
            
            message = f"Для сброса пароля перейдите по ссылке: {reset_link}"
            
            # Используем базовый сервис для отправки уведомления
            self.notify_user(
                user=user,
                message=message,
                notification_type='password_reset',
                subject='Сброс пароля',
                html_message=f"""
                    <p>Для сброса пароля перейдите по ссылке:</p>
                    <p><a href="{reset_link}">Сбросить пароль</a></p>
                    <p>Ссылка действительна в течение 1 часа.</p>
                """
            )
            
            return {'status': 'success', 'email': user.email}
            
        except ObjectDoesNotExist:
            # Не сообщаем, что пользователь не существует (защита от перебора)
            return {'status': 'success', 'email': email}

