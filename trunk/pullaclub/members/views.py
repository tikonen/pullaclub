from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.utils import simplejson
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.views.decorators.http import condition

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from pullaclub.members.models import ApplyForm, UserApplication, UserProfile, Comment, ProfileForm, Topic, create_default_profile, MultiEmailField

def latest_entry(request, page):
    return Comment.objects.latest('datetime').datetime;


@login_required
@condition(last_modified_func=latest_entry) 
def index(request, page):
    
    view_list = []
    error_message = None

    try:
        topic = Topic.objects.latest('datetime')
    except Topic.DoesNotExist:
        topic = None

    pag = Paginator(Comment.objects.filter(parent=None).order_by('-datetime'),10)
    for update in pag.page(int(page)).object_list: # view root level comments with subcomments
        view_list.append({'rootcomment': update,
                          'subcomments': Comment.objects.filter(parent=update.id).order_by('datetime')})
            
    t = loader.get_template('members/members_index.html')
    c = Context({
            'user': request.user,
            'topic': topic,
            'page': pag.page(int(page)),
            'view_list': view_list,
            'member_list': User.objects.exclude(userprofile__user_type='D'),
            'topic_list': Topic.objects.order_by('-datetime')[1:10],
            'application_list': UserApplication.objects.filter(status='P'),
            'error_message': error_message,
            })
    return HttpResponse(t.render(c))

@login_required
def profile(request, userid):
    
    user = get_object_or_404(User,pk=userid)

    success = False
    can_edit = False
    # user can only edit this own profile
    if request.user.is_staff or request.user == user:
        can_edit = True

    if request.method == 'POST':
        # user can only edit this own profile
        if not request.user.is_staff and not request.user == user:
            raise Http404

        form = ProfileForm(request.POST, request.FILES) # form bound to the POST data
        if form.is_valid(): # All validation rules pass                
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']            
            user.save()
                
            profile = user.get_profile()
            profile.description = form.cleaned_data['description']
            uploaded_file = form.cleaned_data['user_image']
            if uploaded_file:                    
                profile.user_image.save(uploaded_file.name, uploaded_file)
            profile.emails = form.cleaned_data['emails']
            profile.save()
            success = True
            #return HttpResponseRedirect(reverse('pullaclub.members.views.index')) # Redirect after POST
        else:
            success = False
    else:
        profile = user.get_profile()
        data = { 'description' : profile.description,
                 'first_name' : user.first_name,
                 'last_name' : user.last_name,
                 'emails' : profile.emails,
                 }
        file_data = {}
        form = ProfileForm(data, file_data)
            
    return render_to_response('members/profile_edit.html', {
            'user': user,
            'form': form,
            'success':success,
            'can_edit' : can_edit,
            'mms_email': settings.POP_USERNAME,
            })


@login_required
def comment(request, action, comment_id):

    if action == 'new' or action == 'edit':

        # new comment
        if request.method == 'POST':
            message = request.POST['message']
            if not message:
                raise Http404
            message = message[:Comment.MAX_LENGTH]

            if action == 'edit':
                if request.user.is_staff:
                    comment = get_object_or_404(Comment,pk=comment_id)
                else:
                    comment = get_object_or_404(Comment,pk=comment_id,user=request.user)
                comment.message = message
                comment.save()
            else: # new comment
                comment = Comment()
                comment.user = request.user
                comment.message = message
                comment.bysource = Comment.BY_WEB
                comment.parent = get_object_or_404(Comment,pk=comment_id)
                comment.save()

            t = loader.get_template('members/single_comment.html')
            c = Context({
                    'comment': comment,
                    })
            response_dict = {
                'url' : request.user.get_profile().user_image.url,
                'description' : request.user.get_profile().description,
                'fullname' : request.user.get_full_name(),
                'message' : comment.message,
                'id' :  comment.parent.id,
                'status': 'new',
                'render' : t.render(c),
                }
                
            return HttpResponse(simplejson.dumps(response_dict), 
                                mimetype='application/javascript')

    elif action == 'delete':
        comment = get_object_or_404(Comment,pk=comment_id,user=request.user)

        if len(Comment.objects.filter(parent=comment)) == 0: # root comment
            comment.delete()
            response_dict = {
                'status' :  'remove',
                }
        else:
            comment.message = "This comment has been deleted"
            comment.image0 = None
            comment.save()
            response_dict = {
                'status' :  'update',
                'message' : comment.message,
                }

        return HttpResponse(simplejson.dumps(response_dict), 
                                mimetype='application/javascript')

    elif action == 'deleteimg':
        comment = get_object_or_404(Comment,pk=comment_id,user=request.user)
        comment.image0 = None
        comment.save()
        response_dict = {
                'status' :  'OK',
        }
        return HttpResponse(simplejson.dumps(response_dict), 
                                mimetype='application/javascript')


    elif action == 'iframe':
        if request.method == 'GET':
            return render_to_response('members/comment_iframe.html')

        # new comment
        message = request.POST['message']
        if not message:
            return render_to_response('members/comment_iframe.html')

        message = message[:Comment.MAX_LENGTH]

        comment = Comment()
        comment.user = request.user
        comment.message = message                
        comment.bysource = Comment.BY_WEB
        if len(request.FILES) > 0:
            # save uploaded file
            uploaded_file = request.FILES['image0']
            comment.image0.save(uploaded_file.name, uploaded_file)
        comment.save()

        return render_to_response('members/comment_iframe.html', {
                'rootcomment': comment,
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
    
@login_required
def topic(request, action):
    
    if request.user.is_staff and action == 'new':
        try:
            if request.method == 'POST':
                message = request.POST['message']
                if not message:
                    raise Http404

                topic = Topic()
                topic.message = message[:Topic.MAX_LENGTH]
                topic.user = request.user
                topic.save()

                response_dict = {
                    'topic' : topic.message,
                    'topic_user' : topic.user.get_full_name(),
                    'topic_time' : 'just now',
                    }
                return HttpResponse(simplejson.dumps(response_dict), 
                                    mimetype='application/javascript')
        except Exception,e:
            print str(e)

    raise Http404

@login_required
def finance(request):
    return render_to_response('members/finance.html', {
            'user': request.user,
            })    

def logoutuser(request):
    logout(request)
    return HttpResponseRedirect('/') 





