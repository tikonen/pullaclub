from django.contrib import admin

from pullaclub.members.models import UserApplication, UserProfile

admin.site.register(UserApplication)
admin.site.register(UserProfile)
