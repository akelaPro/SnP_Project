from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from galery.views import PhotoViewSet, CommentViewSet, VoteViewSet, home, photo_detail
router = routers.DefaultRouter()
router.register(r'api/photos', PhotoViewSet, basename='photo')
router.register(r'api/comments', CommentViewSet, basename='comment')
router.register(r'api/votes', VoteViewSet, basename='vote')

app_name = 'galery'

urlpatterns = [
    path('', home, name='home'),
    path('photo/<int:pk>/', photo_detail, name='photo_detail'),
    path('', include(router.urls)),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)