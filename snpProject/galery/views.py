import os
from django.shortcuts import render

from . models import Photo

from . forms import UploadFileForm

# Create your views here.


def index(request):
    photos = Photo.objects.all()  # Получаем все объекты Photo
    data = {'photos': photos}  # Создаем словарь с ключом 'photos'
    return render(request, 'galery/index.html', data)



def handle_uploaded_file(f):
    upload_dir = 'uploads'
    
    # Проверяем, существует ли директория, если нет - создаем
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Сохраняем файл
    with open(os.path.join(upload_dir, f.name), "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def about(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['file'])
    else:
        form = UploadFileForm()
    return render(request, 'galery/about.html',
                  {'title': 'О сайте', 'form': form})