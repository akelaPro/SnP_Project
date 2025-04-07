# API/services/base_service.py
from service_objects.services import Service
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# from django.core import signals  # УДАЛИТЬ
import logging

from notification.task1 import send_notification_email_task


logger = logging.getLogger(__name__)

class BaseService(Service):
    def notify_user(self, user, message, notification_type, subject=None, **kwargs):
        """
        Базовый метод для отправки уведомлений
        """
        try:
            # Create notification in database
            notification = Notification.objects.create(
                user=user,
                message=message,
                notification_type=notification_type
            )

            # Try WebSocket
            try:
                self._send_websocket_notification(notification)
            except Exception as e:
                logger.error(f"WebSocket notification failed: {str(e)}")

            # Try Email
            try:
                if hasattr(user, 'email') and user.email:
                    send_notification_email_task.delay(
                        notification.id,
                        subject,
                        message,
                        user.email,
                        kwargs.get('html_message'),
                        kwargs.get('photo_title'),
                        kwargs.get('photo_id')
                    )
            except Exception as e:
                logger.error(f"Email notification task failed: {str(e)}")

            return notification
        except Exception as e:
            logger.error(f"Notification creation failed: {str(e)}")
            return None


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

    # def _send_email_notification(self, notification, subject=None, **kwargs): # УДАЛИТЬ
    #     """Отправка уведомления по email через сигналы"""
    #     if hasattr(notification.user, 'email') and notification.user.email: # УДАЛИТЬ
    #         signals.request_started.send( # УДАЛИТЬ
    #             sender=self.__class__, # УДАЛИТЬ
    #             notification_id=notification.id, # УДАЛИТЬ
    #             user_id=notification.user.id, # УДАЛИТЬ
    #             message=notification.message, # УДАЛИТЬ
    #             notification_type=notification.notification_type, # УДАЛИТЬ
    #             subject=subject,  # Передаем subject # УДАЛИТЬ
    #             recipient_email=notification.user.email,  # Передаем recipient_email # УДАЛИТЬ
    #             **kwargs # Передаем дополнительные данные # УДАЛИТЬ
    #         ) # УДАЛИТЬ