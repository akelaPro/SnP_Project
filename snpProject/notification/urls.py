# notification/urls.py

from django.urls import path

from django.conf.urls.static import static
from django.conf import settings
from .views import NotificationViewTemlate
from django.urls import path, include
from rest_framework.routers import DefaultRouter
#from .views import NotificationViewSet


app_name = 'notification'

#router = DefaultRouter()
#router.register(r'notifications', NotificationViewSet, basename='notifications')


urlpatterns = [
    #path('api/', include(router.urls)),
    path('', NotificationViewTemlate.as_view(), name='notification_list'),
]
if settings.DEBUG:
    urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)