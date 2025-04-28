from django.shortcuts import get_object_or_404, render
from django.views import View
from galery.models import Photo
from django.views.generic import TemplateView


def home(request): 
    return render(request, 'galery/index.html')  

def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'galery/photo.html', {'photo': photo})
  

class RegistrationTemplateView(TemplateView):
    template_name = 'galery/registration.html'


class LoginTemplateView(TemplateView):
    template_name = 'galery/login.html'


class CreatePhotoTemlate(TemplateView):
    template_name = 'galery/add_post.html'

class UserProfileView(View):
    def get(self, request):
        return render(request, 'galery/profile.html', {})
    
class Password_reset_request(TemplateView):
    template_name = 'galery/password_reset_request.html'

class Password_reset_confirm(TemplateView):
    template_name = 'galery/password_reset_confirm.html'
