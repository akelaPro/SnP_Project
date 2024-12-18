from django import forms
from django.contrib.auth import get_user_model



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'avatar']