from django.contrib import admin

from pullaclub.members.models import UserApplication, UserProfile, Comment

admin.site.register(UserApplication)
admin.site.register(UserProfile)
admin.site.register(Comment)
