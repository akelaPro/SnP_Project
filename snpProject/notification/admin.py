from django.contrib import admin
from django.contrib import admin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification  
from django.utils import timezone
from .forms import MassNotificationForm  

class NotificationAdmin(admin.ModelAdmin):
    actions = ['send_mass_notification']

    def send_mass_notification(self, request, queryset):
        form = MassNotificationForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            message = form.cleaned_data['message']
            send_to_all = form.cleaned_data['send_to_all']

            channel_layer = get_channel_layer()

            if send_to_all:

                async_to_sync(channel_layer.group_send)(
                    'all_users',
                    {
                        'type': 'mass_notification',
                        'notification': {
                            'message': message,
                            'created_at': timezone.now().isoformat(),
                        }
                    }
                )
                self.message_user(request, "Массовое уведомление успешно отправлено всем пользователям.")
            else:
               
                for user in queryset:
                    group_name = f"user_{user.id}"
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'mass_notification',
                            'notification': {
                                'message': message,
                                'created_at': timezone.now().isoformat(),
                            }
                        }
                    )
                self.message_user(request, "Уведомление успешно отправлено выбранным пользователям.")

        return self.change_view(request, self.get_object(request), form=form)

    send_mass_notification.short_description = "Отправить массовое уведомление"

admin.site.register(Notification, NotificationAdmin)
