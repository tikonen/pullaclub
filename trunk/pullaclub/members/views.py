import math
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from exceptions import Exception
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.utils import simplejson
from django.core.files.uploadedfile import SimpleUploadedFile


from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from pullaclub.members.models import ApplyForm, UserApplication, UserProfile, Comment, ProfileForm, Topic, create_default_profile

def __truncate_length(text,max_length):
    if len(text) > max_length:
        return text[:max_length]
    return text

@login_required
def index(request, offset):
    
    view_list = []
    error_message = None

    try:
        topic = Topic.objects.order_by('-datetime')[0]
    except Topic.DoesNotExist:
        topic = None


    page_len = 9  # number of root comments in single page
    offset = int(offset)
    comment_count = Comment.objects.filter(parent=None).count()
    if comment_count < page_len:
        show_count = comment_count
        page_count = 0
        offset = 0
        active_page = 0
    else:
        active_page=offset
        show_count = page_len
        page_count = int(math.ceil(comment_count / float(page_len)))
        offset *= show_count
        if (offset+show_count) > comment_count:
            show_count = comment_count-offset;

    # page_len root level comments starting from offset
    for update in Comment.objects.filter(parent=None).order_by('-datetime')[offset:offset+show_count]:
        view_list.append({'rootcomment': update,
                          'subcomments': Comment.objects.filter(parent=update.id).order_by('datetime')})
            
    t = loader.get_template('members/members_index.html')
    c = Context({
            'user': request.user,
            'topic': topic,
            'page_count': page_count,
            'active_page': active_page,
            'view_list': view_list,
            'member_list': User.objects.all(),            
            'topic_list': Topic.objects.order_by('-datetime')[1:10],
            'application_list': UserApplication.objects.filter(status='P'),
            'error_message': error_message,
            })
    return HttpResponse(t.render(c))

@login_required
def profile(request, action, username):
    
    can_edit = False

    if action == 'view':
        if request.user.username == username or request.user.is_staff:
            can_edit = True
            pass

        user = get_object_or_404(User,username=username)
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            profile = create_default_profile(user)

        return render_to_response('members/profile.html', {
                'user': user,
                'profile': profile,
                'can_edit' : can_edit,
                })

    elif action == 'edit':

        user = get_object_or_404(User,username=username)

        # user can only edit this own profile
        if not request.user.is_staff and not request.user == user:
            raise Http404

        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES) # form bound to the POST data
            if form.is_valid(): # All validation rules pass
                
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                
                profile = user.get_profile()
                profile.description = form.cleaned_data['description']
                uploaded_file = form.cleaned_data['user_image']
                if uploaded_file:
                    # should validate that it really is an image
                    profile.user_image.save(uploaded_file.name, uploaded_file)

                profile.save()

                return HttpResponseRedirect(reverse('pullaclub.members.views.index')) # Redirect after POST
        else:
            profile = user.get_profile()
            data = { 'description' : profile.description,
                     'first_name' : user.first_name,
                     'last_name' : user.last_name,
                      }
            file_data = {}
            form = ProfileForm(data, file_data)
            
        return render_to_response('members/profile_edit.html', {
                'user': user,
                'form': form,
                })

    raise Http404

@login_required
def comment(request, action, comment_id):
    
    if action == 'new' or action == 'edit':
        # new comment
        if request.method == 'POST':
            message = request.POST['message']
            if not message:
                raise Http404
            message = __truncate_length(message,Comment.MAX_LENGTH)

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
            response_dict = {
                'url' : request.user.get_profile().user_image.url,
                'description' : request.user.get_profile().description,
                'username' : request.user.username,
                'fullname' : request.user.get_full_name(),
                'message' : comment.message,
                'id' :  parentid,
                'render' : t.render(c),
                }
                
            return HttpResponse(simplejson.dumps(response_dict), 
                                mimetype='application/javascript')



    elif action == 'delete':
        comment = get_object_or_404(Comment,pk=comment_id,user=request.user)
        comment.message = "This comment has been deleted"
        comment.save()
        response_dict = {
                'status' :  'OK',
        }
        return HttpResponse(simplejson.dumps(response_dict), 
                                mimetype='application/javascript')

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
    
@login_required
def topic(request, action):
    
    # TODO: validate message and escape code it!
    if request.user.is_staff and action == 'new':
        try:
            if request.method == 'POST':
                message = request.POST['message']
                if not message:
                    raise Http404

                topic = Topic()
                topic.message = __truncate_length(message,Topic.MAX_LENGTH)
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





