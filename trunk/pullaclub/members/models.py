import os
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File


class UserProfile(models.Model):
    
    DEFAULT_LEVEL = 'NE'
    DEFAULT_IMAGE='default.jpg'

    user = models.ForeignKey(User, unique=True)

    # should use ImageField here but it requires Python Imaging Library
    user_image = models.FileField(upload_to='photos')
    #user_level = models.CharField(max_length=2,choices=USER_LEVELS)
    description = models.CharField(max_length=15, blank=True)

    def __unicode__(self):
        return "Profile of '"+str(self.user)+"'"

class Topic(models.Model):

    user = models.ForeignKey(User)
    message = models.CharField(max_length=160)
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + ": "+self.message


class Comment(models.Model):

    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, blank=True)
    message = models.CharField(max_length=160)
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + ": "+self.message[:30]

class UserApplication(models.Model):

    APPLICATION_STATES = (
        ('P','Pending'),
        ('R','Rejected'),
        ('A','Accepted'),
    )

    name = models.CharField(max_length=30)
    email = models.EmailField()
    referral = models.CharField(max_length=30)
    message = models.CharField(max_length=160)
    status = models.CharField(max_length=1,choices=APPLICATION_STATES)

    def __unicode__(self):
        return "Application from "+self.name

class ProfileForm(forms.Form):
    user_image = forms.FileField(required=False)
    description = forms.CharField(max_length=15)


class ApplyForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    referral = forms.CharField()
    message = forms.CharField(max_length=160,
                              widget=forms.Textarea(attrs={'rows':4, 'cols':60}))

def create_default_profile(user):
    # create default profile
    profile = UserProfile()
    profile.user = user
    defaultpic = open(os.path.join(settings.MEDIA_ROOT,settings.DEFAULT_IMAGE),'r');
    profile.user_image.save(settings.DEFAULT_IMAGE,File(defaultpic))
    defaultpic.close()
    profile.save()
    profile.description = 'Pikkupulla'
    profile.save()
    return profile

from django.db.models.signals import post_save

def user_created_signal(sender, **kwargs):
    # Note that django sometimes likes to call twice signals, so
    # remember to avoid creating double profiles.
    if kwargs['created']:
        user = kwargs['instance']
        try:
            user.get_profile()
            #user.get_user_profile()
        except UserProfile.DoesNotExist:
            create_default_profile(user)

post_save.connect(user_created_signal, sender=User)
