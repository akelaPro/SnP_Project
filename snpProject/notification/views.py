

from django.shortcuts import render
from django.views import View


class NotificationView(View):
    def get(self, request):
        notifications = request.user.notifications.all()
        return render(request, 'notification/notifications.html', {'notifications': notifications})
