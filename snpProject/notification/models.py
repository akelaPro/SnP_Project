from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import signals

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, default="уведомление")
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Уведомление для {self.user.email}"

    def send_email_notification(self):
        if not self.email_sent and hasattr(self.user, 'email') and self.user.email:
            subject = f"Новое уведомление: {self.notification_type}"
            html_message = render_to_string('notification/email_notification.html', {
                'notification': self,
                'site_url': settings.SITE_URL
            })
            plain_message = strip_tags(html_message)
            
            # Используем сигналы вместо прямого импорта
            signals.request_started.send(
                sender=self.__class__,
                notification_id=self.id,
                subject=subject,
                message=plain_message,
                recipient_email=self.user.email,
                html_message=html_message
            )