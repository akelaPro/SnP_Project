import os
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from snpProject import settings
from .models import Photo, Comment, Vote
from .forms import AddPostForm, UploadFileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView


class PhotoHome(ListView):
    model = Photo
    template_name = 'galery/index.html'
    context_object_name = 'photos'
    extra_conext = {'default_image': settings.DEFAULT_USER_IMAGE,}
    def get_queryset(self):
        return Photo.objects.all() 


class CustomLogoutView(LogoutView):
    next_page = 'home'




class AddPage(CreateView):
    form_class = AddPostForm
    template_name = 'galery/add_post.html'
    title_page = 'Добавление статьи'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
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
            Comment.objects.create(text=comment_text, author=request.user, photo=photo)
            return HttpResponseRedirect(reverse('photo_detail', args=[photo_id]))
        else:
            return HttpResponseRedirect(reverse('login'))



class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'galery/photo.html'
    context_object_name = 'photo'  # Здесь мы указываем, что объект будет доступен как 'photo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.photo = self.object  # Получаем объект фотографии
        context['comments'] = Comment.objects.filter(photo=self.photo)  # Получаем комментарии к фотографии
        context['likes_count'] = self.photo.votes.count()  # Количество лайков
        context['has_liked'] = self.has_liked(self.request.user, self.photo.id)  # Проверяем, лайкнул ли пользователь
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
    def post(self, request, pk):  # Измените photo_id на pk
        photo = get_object_or_404(Photo, id=pk)  # Используйте pk здесь
        vote_handler = VoteHandler(request.user, pk)  # Используйте pk здесь

        if vote_handler.can_vote():
            vote_handler.add_vote()

        return redirect(reverse('photo_detail', kwargs={'pk': photo.id}))

    
class RemoveVoteView(View):
    def post(self, request, pk):  # Измените photo_id на pk
        if request.user.is_authenticated:
            photo = get_object_or_404(Photo, id=pk)  # Используйте pk здесь
            try:
                vote = Vote.objects.get(author=request.user, photo=photo)
                vote.delete()
            except Vote.DoesNotExist:
                pass 
        return redirect('photo_detail', pk=pk)  # Используйте pk здесь
