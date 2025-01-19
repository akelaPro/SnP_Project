# notification/urls.py

from django.urls import path
from .views import NotificationView

app_name = 'notification'

urlpatterns = [
    path('', NotificationView.as_view(), name='notification_list'),
]
