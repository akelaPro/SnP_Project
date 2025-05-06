from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
import logging
from django.template.loader import render_to_string # Import render_to_string
from django.utils.html import strip_tags # Import strip_tags

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='notification.send_notification_email')
def send_notification_email_task(self, notification_id, subject, message, recipient_email, html_message=None, photo_title=None, photo_id=None):
    try:
        if not getattr(settings, 'EMAIL_ENABLED', False):
            logger.warning("Email notifications are disabled in settings")
            return

        logger.info(f"Attempting to send email to {recipient_email}")
        
        # Рендерим шаблон
        html_message = render_to_string('notification/email_notification.html', {
            'subject': subject, # Передаем subject
            'message': message, # Передаем message
            'photo_title': photo_title, # Передаем photo_title
            'photo_id': photo_id, # Передаем photo_id
            'site_url': settings.SITE_URL
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
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