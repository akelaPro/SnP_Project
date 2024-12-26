from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views 
from .views import AddCommentView, AddPostView, AddVoteView, PhotoDetailView, RemoveVoteView

app_name = 'galery'

urlpatterns = [
    path('', views.PhotoHome.as_view(), name='home'),
    path('author_photo/<int:author_id>/', views.PhotoAuthor.as_view(), name='author_photo_id'),
    path('author_comment/<int:author_id>/', views.PhotoComment.as_view(), name='author_comment_comment'),
    path('photo/<int:photo_id>/add_comment/', AddCommentView.as_view(), name='add_comment'),
    path('photo/<int:pk>/', PhotoDetailView.as_view(), name='photo_detail'),
    path('photo/<int:photo_id>/add_vote/', AddVoteView.as_view(), name='add_vote'),
    path('add-post/', AddPostView.as_view(), name='add_post'),
    path('photo/<int:photo_id>/remove_vote/', views.RemoveVoteView.as_view(), name='remove_vote'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


