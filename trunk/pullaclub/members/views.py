from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from exceptions import Exception
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from pullaclub.members.models import ApplyForm, UserApplication, UserProfile

def index(request):
    
    view_list = []
    error_message = None
    DEFAULT_PROFILE_URL=settings.MEDIA_URL+'default.jpg'

    for user in User.objects.all():        
        try:
            profile = user.get_profile()
            profile_url = profile.user_image.url
        except UserProfile.DoesNotExist:
            profile_url = DEFAULT_PROFILE_URL

        view_list.append({'user':user, 'profile_url':profile_url})
    

    t = loader.get_template('members/members_index.html')
    c = Context({
            'user_name': request.user.get_full_name(),
            'view_list': view_list,
            'error_message': error_message,
            })
    return HttpResponse(t.render(c))

def apply(request):

    if request.method == 'POST': # If the form has been submitted...
        form = ApplyForm(request.POST) # form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
        
            application = UserApplication()
            application.name = form.cleaned_data['name']
            application.email = form.cleaned_data['email']
            application.referral = form.cleaned_data['referral']
            application.message = form.cleaned_data['message']
            application.status = 'P'
            application.save()
            #return HttpResponseRedirect(reverse('members.views.index')) # Redirect after POST
            return HttpResponseRedirect("/thankyou.html") # Redirect after POST
    else:
        form = ApplyForm() # An unbound form

    return render_to_response('members/apply.html', {
            'form': form,
            })
    

def logoutuser(request):
    logout(request)
    return HttpResponseRedirect('/') 

index = login_required(index)

