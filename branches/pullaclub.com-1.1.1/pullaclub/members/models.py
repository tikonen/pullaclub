import os
import re

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File

email_re = re.compile(r"[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}",re.IGNORECASE)

class UserProfile(models.Model):
    
    USER_TYPE = (
        ('S','Active'),
        ('A','Alumni'),
        ('H','Honorary'),
        ('D','System')
    )

    USER_ORG = (
        ('AWS','Airwide Solutions'),
        ('EXT','External'),
    )

    user = models.ForeignKey(User, unique=True)

    user_image = models.ImageField(upload_to=settings.PHOTO_UPLOAD_DIR)
    user_type = models.CharField(max_length=2,choices=USER_TYPE,null=True)
    description = models.CharField(max_length=15, blank=True)
    organization = models.CharField(max_length=30,choices=USER_ORG,blank=True)
    user = models.ForeignKey(User)
    emails = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        return "'"+str(self.user)+"@"+self.organization+"'"

    def user_class(self):
        if self.user_type == 'D':
            return 'sys_name'
        if self.organization == 'AWS':
            return 'user_name'
        else:
            return 'ext_name'


    def user_type_desc(self):
        if self.organization == 'EXT':
            return "External"
        if self.user.is_staff:
            return "Staff"
        elif self.user_type == 'D':
            return 'System'
        elif self.user_type == 'A':
            return 'Alumni'
        elif self.user_type == 'H':
            return 'Honorary'
        return 'Member'


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

    BY_EMAIL = 'E'
    BY_MOBILE = 'M'
    BY_WEB = 'W'
    BY_API = 'A'
    BY_OTHER = 'O'

    BY_SOURCES = (
        (BY_EMAIL,'E-Mail'),
        (BY_MOBILE,'Mobile'),
        (BY_WEB,'Web'),
        (BY_API,'API'),
        (BY_OTHER,'Other'),
    )

    MAX_LENGTH=500

    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, blank=True)
    message = models.CharField(max_length=MAX_LENGTH)
    image0 = models.ImageField(upload_to=settings.COMMENT_IMAGE_UPLOAD_DIR, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    bysource = models.CharField(max_length=1,choices=BY_SOURCES)
    bysource_detail = models.CharField(max_length=100,null=True,blank=True)

    def __unicode__(self):
        return self.user.username + ": "+self.message[:30]

    def get_source_desc(self):
        for source in self.BY_SOURCES:
            if source[0] == self.bysource:
                return source[1]
        return 'Unknown'

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

from django.forms.util import ValidationError
class MultiEmailField(forms.CharField):

    default_error_messages = {
        'invalid': (u'Enter a valid e-mail address.'),
    }

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        super(MultiEmailField, self).__init__(*args, **kwargs)

    def clean(self, value):
        "Check if value consists only of valid emails."
        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).clean(value)
        cleaned = ''
        for email in re.split(' |\n|,|;',value):
            email = email.strip().lower()
            if not email == '':
                if not email_re.match(email):
                    raise ValidationError('\''+email + '\' is not a valid e-mail')

        return re.sub(r'[;, \n]+','\n',value).lower().strip()  # separated by newline


class ProfileForm(forms.Form):

    user_image = forms.ImageField(required=False)
    description = forms.CharField(max_length=15)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30,required=False)

    emails = MultiEmailField(label='E-mail addresses', required=False,
                             max_length=500,
                             widget=forms.Textarea(attrs={'rows':4, 'cols':50}))


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
        (_, suffix) = os.path.splitext(settings.DEFAULT_IMAGE)
        profile.user_image.save(str(user.id)+suffix,File(defaultpic))
    except IOError:
        # something should be done here
        pass

    defaultpic.close()

    profile.emails = user.email
    profile.description = settings.DEFAULT_USER_DESCRIPTION
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
