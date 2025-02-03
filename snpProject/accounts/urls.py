from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts import views #import UpdateUserProfileAPIView, UserPhotosAPIView, UserProfileAPIView, UserProfileView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('api/auth/', include('djoser.urls')),  
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('api/auth/logout/', include('djoser.urls.authtoken')),
    path('api/user/profile/', views.UserProfileAPIView.as_view(), name='user_profile'),
    path('api/user/photos/', views.UserPhotosAPIView.as_view(), name='user_photos'),
    path('api/auth/register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.LoginTemplateView.as_view(), name='login_template'),
    path('register/', views.RegistrationTemplateView.as_view(), name='registration_template'),
    path('api/user/profile/update/', views.UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
]

