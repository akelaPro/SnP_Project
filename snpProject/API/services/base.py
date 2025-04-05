from service_objects.services import Service
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core import signals
import logging

logger = logging.getLogger(__name__)

class BaseService(Service):
    def notify_user(self, user, message, notification_type, subject=None):
        """
    Базовый метод для отправки уведомлений через:
    1. Сохранение в БД
    2. WebSocket
    3. Email
        """
        try:
            # Создаем уведомление в базе данных
            notification = Notification.objects.create(
            user=user,
            message=message,
            notification_type=notification_type
        )
        
        # Отправляем уведомление через WebSocket
            self._send_websocket_notification(notification)
        
        # Отправляем email уведомление
            self._send_email_notification(notification, subject)  # Передаем subject
        
            return notification
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}", exc_info=True)
            raise


    def _send_websocket_notification(self, notification):
        """Отправка уведомления через WebSocket"""
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{notification.user.id}",
                {
                    'type': 'send_notification',
                    'notification': {
                        'id': notification.id,
                        'message': notification.message,
                        'notification_type': notification.notification_type,
                        'created_at': notification.created_at.isoformat(),
                        'is_read': notification.is_read
                    }
                }
            )
        except Exception as e:
            logger.error(f"WebSocket notification error: {str(e)}", exc_info=True)

    def _send_email_notification(self, notification, subject=None):
        """Отправка уведомления по email через сигналы"""
        if hasattr(notification.user, 'email') and notification.user.email:
            signals.request_started.send(
                sender=self.__class__,
                notification_id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                notification_type=notification.notification_type,
                subject=subject,  # Передаем subject
                recipient_email=notification.user.email  # Передаем recipient_email
            )
