# notification/urls.py

from django.urls import path

from django.conf.urls.static import static
from django.conf import settings
from .views import NotificationView

app_name = 'notification'

urlpatterns = [
    path('', NotificationView.as_view(), name='notification_list'),
]
if settings.DEBUG:
    urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)