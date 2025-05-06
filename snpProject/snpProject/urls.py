from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('API.urls', namespace='API')),  # Добавлен trailing slash
    path('', include('galery.urls', namespace='galery')),  # Изменено с '/' на ''
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('notifications/', include('notification.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]