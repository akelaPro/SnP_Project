from django.utils import timezone
import os
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.db.models import Count

from snpProject import settings
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from galery.models import *
from notification.models import Notification
from galery.task import delete_photo

from .forms import AddPostForm, UploadFileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.views.generic import  ListView, DetailView, FormView, CreateView, UpdateView



class PhotoHome(ListView):
    model = Photo
    template_name = 'galery/index.html'
    context_object_name = 'photos'

    def get_queryset(self):
        queryset = Photo.objects.filter(moderation='3')
    

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) | 
                Q(author__username__icontains=search_query)
            )

        
    

        sort_option = self.request.GET.get('sort', '')  
        if sort_option == 'votes':
            queryset = queryset.annotate(vote_count=Count('votes')).order_by('-vote_count')
        elif sort_option == 'date':
            queryset = queryset.order_by('-published_at')  
        elif sort_option == 'comments':
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_photo'] = settings.DEFAULT_PHOTO_IMAGE
        context['default_image'] = settings.DEFAULT_USER_IMAGE
        return context

class AddPostView(CreateView):
    model = Photo
    form_class = AddPostForm
    template_name = 'galery/add_post.html'
    success_url = reverse_lazy('galery:home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        photo = form.save()
        return super().form_valid(form)


class PhotoAuthor(ListView):
    template_name = 'galery/index.html'
    context_object_name = 'photos'
    allow_empty = False

    def get_queryset(self):
        return Photo.objects.filter(author__id=self.kwargs['author_photo_id'])
    

class PhotoComment(ListView):
    template_name = 'galery/index.html'
    context_object_name = 'comments'
    allow_empty = False
    
    def get_queryset(self):
        return Comment.objects.filter(photo__id=self.kwargs['author_comment_id'])




class AddCommentView(View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        comment_text = request.POST.get('text')
        
        if request.user.is_authenticated:
            comment = Comment.objects.create(text=comment_text, author=request.user, photo=photo)
            # Отправка уведомления автору фотографии
            self.notify_user(photo.author, f"Новый комментарий на вашу фотографию '{photo.title}': {comment.text}", 'new_comment')
            return JsonResponse({
                'success': True,
                'comment': {
                    'author': comment.author.username,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S") 
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Пользователь не авторизован'})

    def notify_user(self, user, message, notification_type):
        notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )
    
    


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'galery/photo.html'
    context_object_name = 'photo'
    pk_url_kwarg = 'photo_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.photo = self.object  
        context['comments'] = Comment.objects.filter(photo=self.photo)  
        context['likes_count'] = self.photo.votes.count()  
        context['has_liked'] = self.has_liked(self.request.user, self.photo.id)
        context['default_image'] = settings.DEFAULT_USER_IMAGE
        return context 

    def has_liked(self, user, photo_id):
        if user.is_authenticated:
            return Vote.objects.filter(author=user, photo_id=photo_id).exists()
        return False
    

    
class VoteHandler:
    def __init__(self, user, photo_id):
        self.user = user
        self.photo = get_object_or_404(Photo, id=photo_id)

    def can_vote(self):
        return self.user.is_authenticated and not Vote.objects.filter(author=self.user, photo=self.photo).exists()

    def add_vote(self):
        if self.can_vote():
            Vote.objects.create(author=self.user, photo=self.photo)




class AddVoteView(View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        if request.user.is_authenticated:
            if not Vote.objects.filter(author=request.user, photo=photo).exists():
                Vote.objects.create(author=request.user, photo=photo)
                # Отправка уведомления автору фотографии
                self.notify_user(photo.author, f"Ваша фотография '{photo.title}' получила новый лайк!", 'new_like')
                return JsonResponse({'success': True, 'likes_count': photo.votes.count()})
            else:
                return JsonResponse({'success': False, 'error': 'Вы уже проголосовали.'})
        return JsonResponse({'success': False, 'error': 'Пользователь не авторизован'})

    def notify_user(self, user, message, notification_type):
        notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )

class RemoveVoteView(View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        
        if request.user.is_authenticated:
            try:

                vote = Vote.objects.get(author=request.user, photo=photo)
                vote.delete()
                

                return JsonResponse({'success': True, 'likes_count': photo.votes.count()})
            except Vote.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Голос не найден.'})
        return JsonResponse({'success': False, 'error': 'Пользователь не авторизован'})



class DeletePhotoView(View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        photo.moderation = '1'  # Статус "Помечена на удаление"
        photo.deleted_at = timezone.now()  # Установите время удаления
        photo.save()
        # Отправка уведомления автору фотографии
        delete_photo.apply_async((photo_id,), countdown= 60)
        self.notify_user(photo.author, f"Ваша фотография '{photo.title}' помечена на удаление.", 'photo_deleted')
        return JsonResponse({'success': True, 'message': 'Фотография помечена на удаление.'})

    def notify_user(self, user, message, notification_type):
        notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )



class RestorePhotoView(View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        if photo.deleted_at and timezone.now() < photo.deleted_at + timezone.timedelta(days=1):
            photo.deleted_at = None  # Сбросить время удаления
            photo.moderation = '2'
            photo.save()
            return JsonResponse({'success': True, 'message': 'Фотография восстановлена.'})
        return JsonResponse({'success': False, 'error': 'Восстановление невозможно.'})