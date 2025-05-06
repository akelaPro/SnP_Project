from django import forms

from . models import Photo, User


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        



class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'avatar']
        widgets = {
            'password': forms.PasswordInput(),
        }



class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Файл")