from django.dispatch import receiver
from django.core import signals
from .task1 import send_notification_email_task

@receiver(signals.request_started)
def handle_notification_email(sender, **kwargs):
    if 'notification_id' in kwargs:
        send_notification_email_task.delay(
            kwargs['notification_id'],
            kwargs['subject'],
            kwargs['message'],
            kwargs['recipient_email'],
            kwargs.get('html_message')
        )