from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse, reverse_lazy
from django.views import View
from django.shortcuts import render, redirect

from snpProject import settings
from galery.models import Photo
from .forms import AddPostForm, USerProfileForm, UserRegistrationForm 
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView


class UserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        return render(request, 'accounts/registration.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return HttpResponseRedirect(reverse('accounts:login'))
        return render(request, 'accounts/registration.html', {'form': form})

    




class UserLoginView(LoginView):
    template_name = 'accounts/login.html'  
    success_url = reverse_lazy('home')


class UserProfile(UpdateView):
    model = get_user_model()
    form_class = USerProfileForm
    template_name = 'accounts/profile.html'
    extra_context = {
        'title': "Профиль пользователя",
        'default_image': settings.DEFAULT_USER_IMAGE,
        'add_post_form': AddPostForm(),
    }

    def get_success_url(self):
        return reverse_lazy('galery:home')  # Перенаправление на главную страницу

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)

    

    


class AddPostView(UpdateView):
    model = Photo
    form_class = AddPostForm
    template_name = 'galery/add_post.html'
    success_url = reverse_lazy('galery:home') 

    def form_valid(self, form):
        form.instance.author = self.request.user  # Установите автора поста
        return super().form_valid(form)
    

