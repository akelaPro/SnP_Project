from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework import routers
from API.views import PhotoViewSet, CommentViewSet, VoteViewSet
from API.views import *

router = routers.DefaultRouter()
router.register(r'api/photos', PhotoViewSet, basename='photo')
router.register(r'api/comments', CommentViewSet, basename='comment')
router.register(r'api/votes', VoteViewSet, basename='vote')

app_name = 'API'

urlpatterns = [
    path('', include(router.urls)),
    path('api/register/', RegistrationAPIView.as_view(), name='register'),
    path('api/auth/verify/', VerifyTokenView.as_view(), name='verify-token'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/refresh/', RefreshView.as_view(), name='refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    #re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('api/user/profile/update/', UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
    path('api/user/profile/', UserProfileAPIView.as_view(), name='user_profile'),
    path('api/user/photos/', UserLisPhoto.as_view(), name='user_photos'),

    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)