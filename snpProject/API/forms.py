from django import forms

class PhotoForm(forms.Form):
    title = forms.CharField(max_length=255, label='Заголовок')
    description = forms.CharField(widget=forms.Textarea, label='Описание')
    image = forms.ImageField(label='Фотография')
