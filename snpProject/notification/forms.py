# notification/forms.py
# notification/forms.py
from django import forms

class MassNotificationForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")
    send_to_all = forms.BooleanField(required=False, label="Отправить всем пользователям")

