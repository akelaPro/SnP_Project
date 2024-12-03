from django import forms

from . models import Photo


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'author', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise forms.ValidationError("Длина превышает 50 символов")

        return title


class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Файл")