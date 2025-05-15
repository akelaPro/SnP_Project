from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from notification.models import Notification
from notification.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated

class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Требуется аутентификация

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)  # Сериализация данных
        return Response(serializer.data)
    
class UnreadNotificationCountView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, request):
            count = Notification.objects.filter(user=request.user, is_read=False).count()
            return Response({'count': count})