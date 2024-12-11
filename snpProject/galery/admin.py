from django.contrib import admin
from django.contrib.admin.models import LogEntry
from . models import Photo, User, Vote, Comment

admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Photo)



