import os
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.db.models import Count

from snpProject import settings
from django.db.models import Q
from .models import Photo, Comment, Vote
from .forms import AddPostForm, UploadFileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView



class PhotoHome(ListView):
    model = Photo
    template_name = 'galery/index.html'
    context_object_name = 'photos'

    def get_queryset(self):
        queryset = Photo.objects.all()
    

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
        return context

class AddPostView(CreateView):
    model = Photo
    form_class = AddPostForm
    template_name = 'galery/add_post.html'
    success_url = reverse_lazy('galery:home') 
    def form_valid(self, form):
        form.instance.author = self.request.user  
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


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'galery/photo.html'
    context_object_name = 'photo'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.photo = self.object  
        context['comments'] = Comment.objects.filter(photo=self.photo)  
        context['likes_count'] = self.photo.votes.count()  
        context['has_liked'] = self.has_liked(self.request.user, self.photo.id) 
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
                return JsonResponse({'success': True, 'likes_count': photo.votes.count()})
            else:
                return JsonResponse({'success': False, 'error': 'Вы уже проголосовали.'})
        return JsonResponse({'success': False, 'error': 'Пользователь не авторизован'})

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
