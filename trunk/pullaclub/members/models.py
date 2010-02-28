from django.db import models
from django import forms
from django.contrib.auth.models import User

class UserProfile(models.Model):

    user = models.ForeignKey(User, unique=True)

    # should use ImageField here but it requires Python Imaging Library
    user_image = models.FileField(upload_to='photos',blank=True)

    def __unicode__(self):
        return "Profile of '"+str(self.user)+"'"

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


class ApplyForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    referral = forms.CharField()
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows':4, 'cols':60}))


from django.db.models.signals import post_save

def user_created_signal(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        # currently nothing here but this is one possible place to
        # create new UserProfile instance
        #
        # Note that django sometimes likes to call twice signals, so
        # remember to avoid creating double profiles.
        pass


post_save.connect(user_created_signal, sender=User)
