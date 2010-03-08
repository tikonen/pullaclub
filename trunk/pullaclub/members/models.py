import os
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File


class UserProfile(models.Model):
    
    user = models.ForeignKey(User, unique=True)

    # should use ImageField here but it requires Python Imaging Library
    user_image = models.FileField(upload_to='photos')
    #user_level = models.CharField(max_length=2,choices=USER_LEVELS)
    description = models.CharField(max_length=15, blank=True)

    def __unicode__(self):
        return "Profile of '"+str(self.user)+"'"

class Topic(models.Model):

    MAX_LENGTH=160

    user = models.ForeignKey(User)
    message = models.CharField(max_length=MAX_LENGTH)
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + ": "+self.message

    def as_truncated(self):
        trunc_len = 30
        if len(self.message) > trunc_len:
            return self.message[:(trunc_len-3)]+'...'
        return self.message


class Comment(models.Model):

    MAX_LENGTH=500

    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, blank=True)
    message = models.CharField(max_length=MAX_LENGTH)
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
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30,required=False)


class ApplyForm(forms.Form):
    name = forms.CharField(label="Full Name")
    email = forms.EmailField(label="E-Mail")
    referral = forms.CharField(label="Recommender")
    message = forms.CharField(max_length=160,
                              widget=forms.Textarea(attrs={'rows':4, 'cols':60}))

def create_default_profile(user):
    # create default profile
    profile = UserProfile()
    profile.user = user
    try:
        # set default user picture
        defaultpic = open(os.path.join(settings.MEDIA_ROOT,settings.DEFAULT_IMAGE),'r');
        (name, suffix) = os.path.splitext(settings.DEFAULT_IMAGE)
        profile.user_image.save(user.username+suffix,File(defaultpic))
    except IOError:
        # something should be done here
        pass
    defaultpic.close()
    profile.save()
    profile.description = 'Pikkupulla'
    profile.save()
    return profile

from django.db.models.signals import post_save

def user_created_signal(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        try:
            # Note that django sometimes likes to call  signals twice, so
            #  avoid creating double profiles.
            user.get_profile()
        except UserProfile.DoesNotExist:
            create_default_profile(user)

post_save.connect(user_created_signal, sender=User)
