from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse, reverse_lazy
from django.views import View
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm 
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model


class UserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        return render(request, 'accounts/registration.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return HttpResponseRedirect(reverse('accounts:login'))
        return render(request, 'accounts/registration.html', {'form': form})



class UserLoginView(LoginView):
    template_name = 'accounts/login.html'  
    success_url = reverse_lazy('home') 

    