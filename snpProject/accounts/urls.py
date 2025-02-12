from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
    path('api/v1/auth/', include('djoser.urls')),  # new
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('api/user/profile/', views.UserProfileAPIView.as_view(), name='user_profile'),
    path('api/user/photos/', views.UserPhotosAPIView.as_view(), name='user_photos'),
    path('api/user/profile/update/', views.UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
    path('login/', views.LoginTemplateView.as_view(), name='login_template'),
    path('register/', views.RegistrationTemplateView.as_view(), name='registration_template'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)