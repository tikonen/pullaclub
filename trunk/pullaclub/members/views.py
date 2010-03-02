from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from exceptions import Exception
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.utils import simplejson

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from pullaclub.members.models import ApplyForm, UserApplication, UserProfile, Comment

def index(request):
    
    view_list = []
    error_message = None

    # 10 latest root level comments
    for update in Comment.objects.filter(parent=None).order_by('-datetime')[:10]:
        view_list.append({'rootcomment': update,
                          'subcomments': Comment.objects.filter(parent=update.id).order_by('datetime')})
            
    t = loader.get_template('members/members_index.html')
    c = Context({
            'user': request.user,
            'view_list': view_list,
            'error_message': error_message,
            })
    return HttpResponse(t.render(c))

def profile(request, action, username):
    
    profile = None

    if action == 'view':
        if request.user.username == username:
            # looking own profile
            pass

        user = get_object_or_404(User,username=username)
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            raise Http404

        return render_to_response('members/profile.html', {
                'user': user,
                'profile': profile,
                })

    raise Http404

def comment(request, action, comment_id):
    
    # TODO: validate message and escape code it!
    if action == 'new' or action == 'pullaa':
        # new comment
        if request.method == 'POST':
            message = request.POST['message']
            if not message:
                message = 'Pullaa!'
            #message.length
            comment = Comment()
            comment.user = request.user
            comment.message = message
            if comment_id == '0': # root comment
                comment.parent = None
            else: # normal comment
                targetcomment = get_object_or_404(Comment,pk=comment_id)
                comment.parent = targetcomment

            comment.save()

            parentid = 0
            rootcomment = None
            subcomment = None
            if comment.parent == None:
                rootcomment = comment
            else:
                subcomment = comment
                parentid = comment.parent.id

            t = loader.get_template('members/single_comment.html')
            c = Context({
                    'rootcomment': rootcomment,
                    'comment': subcomment,
                    })
            print(t.render(c))

            response_dict = {
                'url' : request.user.get_profile().user_image.url,
                'description' : request.user.get_profile().description,
                'username' : request.user.username,
                'fullname' : request.user.get_full_name(),
                'message' : comment.message,
                'id' :  parentid,
                'render' : t.render(c),
                }
                
            #return HttpResponse("OK")
            return HttpResponse(simplejson.dumps(response_dict), 
                                mimetype='application/javascript')



    elif action == 'delete':
        # TODO check that user owns comment
        comment = get_object_or_404(Comment,pk=comment_id)
        comment.delete()
        return HttpResponse(str(comment.id))

    elif action == 'view':
        comment = get_object_or_404(Comment,pk=comment_id)
        return render_to_response('members/single_comment.html',
                                  { 'rootcomment': comment,
                                    'comment' : None,
                                    })

    raise Http404


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
profile = login_required(profile)
comment = login_required(comment)

