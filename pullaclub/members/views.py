import re
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
#from django.views.decorators.cache import cache_control, cache_page

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from pullaclub.members.models import ApplyForm, UserApplication, UserProfile, Comment, ProfileForm, Topic, create_default_profile, MultiEmailField

def _vote_cookie(vote_id):
    return 'voted'+str(vote_id)

def latest_comment(request, **kwargs):
    return Comment.objects.latest('datetime').datetime;

@login_required
@condition(last_modified_func=latest_comment) 
def index(request, page):
    
    view_list = []
    error_message = None

    try:
        topic = Topic.objects.latest('datetime')
    except Topic.DoesNotExist:
        topic = None

    pag = Paginator(Comment.objects.filter(parent=None).order_by('-datetime'),10)
    for update in pag.page(int(page)).object_list: # view root level comments with subcomments
        if update.is_poll(): # update the voting status
            vkey = _vote_cookie(update.id)
            # rely in cookie on user specific vote status check
            update.has_voted = vkey in request.session and request.session[vkey] == 'true'
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
@condition(last_modified_func=latest_comment) 
def latest(request, latestid):
    latestid = int(latestid)

    view_list = []
    response_dict = {}
    newupdates = []
    # find root level comments that are newer than requested
    # id. Render html that can be appended on the page.
    #
    for update in Comment.objects.filter(parent=None).filter(id__gt=latestid).order_by('-datetime'):
        newupdates.append(update.id)
        view_list.append({'rootcomment': update,
                          'subcomments': Comment.objects.filter(parent=update.id).order_by('datetime')})

    if len(view_list) > 0:
        t = loader.get_template('members/comments.html')
        c = Context({
                'user': request.user,
                'view_list': view_list,
                })
        response_dict['root'] = t.render(c)

    # find subcomments that are newer than request id. render html for each
    for comment in Comment.objects.exclude(parent=None).exclude(parent__in=newupdates).filter(id__gt=latestid).order_by('datetime'):    
        t = loader.get_template('members/sub_comment.html')
        c = Context({
                'user' : request.user,
                'comment': comment,
                })
        response_dict[comment.parent.id] = t.render(c)

    return HttpResponse(simplejson.dumps(response_dict), 
                        mimetype='application/javascript')


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
        if not can_edit:
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


from pullaclub.members.templatetags.custom_tags import lire
def _parse_poll_choices(message):
    # parse listable items from message and build dictionary of poll
    # items
    #
    polld = [{'desc': x[1].strip().capitalize(), 'count':0 } for x in lire.findall(message)]
    if len(polld) > 0:
        idx = 1
        for item in polld:
            item['item'] = idx
            idx += 1
        message = lire.sub('',message) # remove poll items from message text

    return(message,polld)
    
@login_required
def vote(request,comment_id):

    comment = get_object_or_404(Comment,pk=comment_id)

    #import pdb
    #pdb.set_trace()
    request.session[_vote_cookie(comment_id)] = 'true'

    if request.method == 'POST' and 'choice' in request.POST: # new vote        
        # cookie based vote tracking
        try:
            # update vote results with locked table so we do not lose votes
            # because of concurrent updates.
            Comment.objects.lock()     
            polld = simplejson.loads(comment.poll)
            choice = request.POST['choice']
            for item in polld:
                if item['item'] == int(choice):
                    item['count'] += 1
                    comment.poll = simplejson.dumps(polld)
                    comment.save()
                    break
        finally:
            Comment.objects.unlock()

    # if request is GET, just show current voting status

    t = loader.get_template('members/single_vote.html')
    c = Context({
            'comment': comment,
            })
    response_dict = {
        'id' :  comment_id,
        'status': 'new',
        'render' : t.render(c),
        }
                
    return HttpResponse(simplejson.dumps(response_dict), 
                        mimetype='application/javascript')

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

            t = loader.get_template('members/sub_comment.html')
            c = Context({
                    'user' : request.user,
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

    raise Http404

@login_required
def iframe(request):

    if request.method == 'GET':
        return render_to_response('members/comment_iframe.html')

    message = request.POST['message']     # new comment
    if not message:
        return render_to_response('members/comment_iframe.html')

    update = Comment()
    message = message[:Comment.MAX_LENGTH]

    if 'poll' in request.POST and request.POST['poll'] == 'on':  # this is poll
        #import pdb
        #pdb.set_trace()
        # convert message list items to poll json structure if possible
        (message, polld) = _parse_poll_choices(message)
        if len(polld) > 0:
            update.poll = simplejson.dumps(polld)

    update.user = request.user
    update.message = message
    update.bysource = Comment.BY_WEB
    if len(request.FILES) > 0:
        # save uploaded file
        uploaded_file = request.FILES['image0']
        update.image0.save(uploaded_file.name, uploaded_file)

    update.save()
        
    return render_to_response('members/comment_iframe.html', {
            'user': request.user,
            'view_list': [ { 'rootcomment': update } ],
            })


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





