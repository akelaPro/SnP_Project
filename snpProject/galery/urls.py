from django.conf import settings
from django.conf.urls.static import static



from django.urls import include, path

from . import views



urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('addpage/', views.addpage, name='add_page'),
    path('photo/<int:photo_id>/', views.show_photo, name='photo'),  # Добавлены угловые скобки
    path('add_comment/', views.add_comment, name='add_comment'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
