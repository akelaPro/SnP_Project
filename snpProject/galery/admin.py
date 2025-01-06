from django.contrib import admin
from django.contrib.admin.models import LogEntry

from galery.flow import PhotoModerationFlow
from . models import Photo, PhotoModerationProcess, User, Vote, Comment

#admin.site.register(Vote)
#admin.site.register(Comment)
#admin.site.register(User)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image', 'published_at', 'author')
    list_display_links = ('title',)
    list_editable = ('description', 'image',)
    list_per_page = 4
    ordering = ('published_at', )
    search_fields = ('description', 'title')
    list_filter = ('author',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'avatar')
    list_display_links = ('email',)
    list_editable = ('avatar', )
    list_per_page = 4
    ordering = ('created_at', 'email')
    search_fields = ('email',)

@admin.register(Vote)
class Votedmin(admin.ModelAdmin):
    list_display = ('author', 'photo')
    list_display_links = ('author',)
    list_per_page = 4
    ordering = ('author',)
    search_fields = ('author__email',)
    list_filter = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at', 'author', 'photo')
    list_display_links = ('author', )
    list_editable = ('text',)
    list_per_page = 4
    ordering = ('created_at', 'text', 'author')
    search_fields = ('author__email', 'text')
    list_filter = ('author', 'photo',)


@admin.register(PhotoModerationProcess)
class PhotoModerationAdmin(admin.ModelAdmin):
    list_display = ('photo', 'approved', 'rejected')
    list_filter = ('approved', 'rejected')
    search_fields = ('photo__title', 'photo__author__username')

    def get_queryset(self, request):
        return super().get_queryset(request)


