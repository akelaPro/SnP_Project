

from django.shortcuts import redirect, render
from django.views import View
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model


class NotificationView(View):
    def get(self, request):
        notifications = request.user.notifications.all()
        return render(request, 'notification/notifications.html', {'notifications': notifications})


class MassNotificationView(View):
    def post(self, request):
        message = request.POST.get('message')
        notification_type = 'mass_notification'
        user = get_user_model()

        for user in User.objects.all():
            notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    'type': 'send_notification',
                    'notification': {
                        'message': notification.message,
                        'notification_type': notification.notification_type,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
        return redirect('admin:notifications')  # Перенаправление по необходимости