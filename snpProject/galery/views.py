import os
from django.shortcuts import get_object_or_404, redirect, render
from .models import Photo, Comment
from .forms import AddPostForm, UploadFileForm
from django.contrib.auth.decorators import login_required

def index(request):
    photos = Photo.objects.all()
    return render(request, 'galery/index.html', {'photos': photos})



@login_required
def add_comment(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        photo_id = request.POST.get('photo_id')
        
        if text and photo_id:
            photo = get_object_or_404(Photo, id=photo_id)
            Comment.objects.create(text=text, author=request.user, photo=photo)
        
        return redirect('photo', photo_id=photo_id)  


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
    return render(request, 'galery/about.html', {'title': 'О сайте', 'form': form})

def addpage(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddPostForm()
    return render(request, 'galery/add_post.html', {'form': form, 'title': 'Добавить пост'})

def show_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    comments = Comment.objects.filter(photo=photo)  # Исправлено на 'photo=photo'
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(text=text, author=request.user, photo=photo)

    return render(request, 'galery/photo.html', {'photo': photo, 'comments': comments})  # Исправлено на 'comments'