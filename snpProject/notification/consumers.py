# notification/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add("all_users", self.channel_name)  # Добавляем пользователя в группу всех
        await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.channel_layer.group_discard("all_users", self.channel_name)  # Убираем пользователя из группы всех

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps(notification))

    async def mass_notification(self, event):
        notification = event['notification']
        # Отправка уведомления всем пользователям
        await self.channel_layer.group_send(
            "all_users",
            {
                'type': 'send_notification',
                'notification': notification
            }
        )