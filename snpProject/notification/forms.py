# notification/forms.py
# notification/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class MassNotificationForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        label="Пользователи"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Сообщение"
    )

