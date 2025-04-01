# notification/admin.py
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from .models import Notification
from .forms import MassNotificationForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'message')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-mass-notification/', self.admin_site.admin_view(self.send_mass_notification),
        )]
        return custom_urls + urls

    def send_mass_notification(self, request):
        if request.method == 'POST':
            form = MassNotificationForm(request.POST)
            if form.is_valid():
                users = form.cleaned_data['users']
                message = form.cleaned_data['message']
                notification_type = 'mass_notification'
                channel_layer = get_channel_layer()

                for user in users:
                    notification = Notification.objects.create(
                        user=user,
                        message=message,
                        notification_type=notification_type
                    )
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
                self.message_user(request, "Уведомления успешно отправлены.")
                return redirect('admin:notification_notification_changelist')
        else:
            form = MassNotificationForm()

        context = {
            'form': form,
            'opts': self.model._meta,
            'title': 'Отправить массовое уведомление',
        }
        return render(request, 'admin/send_mass_notification.html', context)