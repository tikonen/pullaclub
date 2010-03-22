from django.contrib import admin

from pullaclub.members.models import UserApplication, UserProfile, Comment, Topic

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user','message')
    list_filter = ['datetime','user']
    date_hierarchy = 'datetime'
    
    inlines = [CommentInline]

admin.site.register(UserApplication)
admin.site.register(UserProfile)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Topic)
