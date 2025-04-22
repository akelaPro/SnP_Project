from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from API.views import *



router = routers.DefaultRouter()
router.register(r'photos', PhotoViewSet, basename='photo')  # Убрал начальный /
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'votes', VoteViewSet, basename='vote')

app_name = 'API'

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegistrationAPIView.as_view(), name='register'),  # Убрал начальный /
    path('auth/verify/', VerifyTokenView.as_view(), name='verify-token'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/profile/update/', UpdateUserProfileAPIView.as_view(), name='update_user_profile'),
    path('user/profile/', UserProfileAPIView.as_view(), name='user_profile'),
    path('user/photos/', UserLisPhoto.as_view(), name='user_photos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)