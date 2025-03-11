from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework import routers
from API.views import PhotoViewSet, CommentViewSet, VoteViewSet
from API import views

router = routers.DefaultRouter()
router.register(r'api/photos', PhotoViewSet, basename='photo')
router.register(r'api/comments', CommentViewSet, basename='comment')
router.register(r'api/votes', VoteViewSet, basename='vote')

app_name = 'API'

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    #path('api/photos/upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('api/user/profile/update/', views.UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
    path('api/user/profile/', views.UserProfileAPIView.as_view(), name='user_profile'),
    path('api/user/photos/', views.UserLisPhoto.as_view(), name='user_photos'),
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)