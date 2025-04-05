from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='notification.send_notification_email')
def send_notification_email_task(self, notification_id, subject, message, recipient_email, html_message=None):
    try:
        if not getattr(settings, 'EMAIL_ENABLED', False):
            logger.warning("Email notifications are disabled in settings")
            return

        logger.info(f"Attempting to send email to {recipient_email}")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        Notification.objects.filter(id=notification_id).update(email_sent=True)
        logger.info(f"Email successfully sent to {recipient_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email notification {notification_id}: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=60)