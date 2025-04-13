from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from galery import views
from galery.views import home, photo_detail

app_name = 'galery'

urlpatterns = [
    path('', home, name='home'),  # Изменено с '/' на ''
    path('photo/<int:pk>/', photo_detail, name='photo_detail'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('login/', views.LoginTemplateView.as_view(), name='login_template'),
    path('createphoto', views.CreatePhotoTemlate.as_view(), name='create_photo'),
    path('register/', views.RegistrationTemplateView.as_view(), name='registration_template'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)