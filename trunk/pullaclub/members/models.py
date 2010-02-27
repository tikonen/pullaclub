from django.db import models
from django import forms
from django.contrib.auth.models import User

class UserProfile(models.Model):

    user = models.ForeignKey(User, unique=True)
    pass

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
        return "Application from %s",name


class ApplyForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    referral = forms.CharField()
    message = forms.CharField()

