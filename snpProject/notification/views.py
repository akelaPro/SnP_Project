

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
from django.contrib.auth.mixins import LoginRequiredMixin


class NotificationView(LoginRequiredMixin, View):  # LoginRequiredMixin проверит аутентификацию
    def get(self, request):
        notifications = request.user.notifications.all().order_by("-created_at")  # только свои уведомления
        return render(request, 'notification/notifications.html', {'notifications': notifications})




