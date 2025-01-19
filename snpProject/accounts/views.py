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
    success_url = reverse_lazy('galery:home')


class UserProfile(UpdateView):
    model = get_user_model()
    form_class = USerProfileForm
    template_name = 'accounts/profile.html'
    

    def get_success_url(self):
        return reverse_lazy('galery:home')  
    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.request.user.photos.all() 
        context['title'] = "Профиль пользователя"
        context['default_image'] = settings.DEFAULT_USER_IMAGE
        context['default_photo'] = settings.DEFAULT_PHOTO_IMAGE
        context['add_post_form'] = AddPostForm()
        return context

