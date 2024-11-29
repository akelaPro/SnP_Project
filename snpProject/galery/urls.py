


from django.urls import include, path

from . import views


urlpatterns = [
path('', views.index, name='home'),
path('about/', views.about, name='about'),
]