

from django.shortcuts import redirect, render
from django.views import View
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class NotificationView(View):
    def get(self, request):
        notifications = request.user.notifications.all()
        return render(request, 'notification/notifications.html', {'notifications': notifications})




class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем уведомления по пользователю
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        message = request.data.get('message')
        notification_type = 'mass_notification'
        channel_layer = get_channel_layer()
        
        # Создаем уведомление для всех пользователей
        users = get_user_model().objects.all()
        for user in users:
            notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
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
        return Response({"status": "success", "message": "Уведомление отправлено всем пользователям."})
