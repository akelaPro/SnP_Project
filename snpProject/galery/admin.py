from datetime import timezone
from os import path
from django.contrib import admin
from django.contrib.admin.models import LogEntry

#from galery.flow import PhotoModerationFlow
from galery.models import *
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#admin.site.register(Vote)
#admin.site.register(Comment)
#admin.site.register(User)
from django.utils.html import format_html
from django.contrib import admin
from galery.models import Photo
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from notification.views import MassNotificationView

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'moderation', 'published_at')

    def approve_photos(self, request, queryset):
        for photo in queryset:
            photo.moderation = '3'  # Одобрено
            photo.save()
            self.notify_user(photo.author, f"Ваша фотография '{photo.title}' одобрена.", 'photo_approved')
        self.message_user(request, "Выбранные фотографии были одобрены.")

    def reject_photos(self, request, queryset):
        for photo in queryset:
            photo.moderation = '1'  # Отклонено
            photo.save()
            self.notify_user(photo.author, f"Ваша фотография '{photo.title}' отклонена.", 'photo_rejected')
        self.message_user(request, "Выбранные фотографии были отклонены.")

    def notify_user(self, user, message, notification_type):
        notification = Notification.objects.create(user=user, message=message, notification_type=notification_type)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )





#@admin.register(Photo)
#class PhotoAdmin(admin.ModelAdmin):
    #list_display = ('title', 'description', 'image', 'published_at', 'author', 'moderation')
    #list_display_links = ('title',)
    #list_editable = ('moderation', )
    #list_per_page = 4
    #ordering = ('published_at', )
    #search_fields = ('description', 'title')
    #list_filter = ('author',)


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




