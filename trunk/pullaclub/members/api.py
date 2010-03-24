import base64

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from pullaclub.members.models import Comment

def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """

    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response


def login_required_basicauth(func=None, realm = ""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    You can provide the name of the realm to ask for authentication within.
    """
    def is_authenticated(user):
        return user is not None and user.is_authenticated()

    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     is_authenticated,
                                     realm, *args, **kwargs)
        return wrapper

    if func:
        return view_decorator(func)
    return view_decorator


@login_required_basicauth(realm="PullaClub API")
def api_comment(request, action, comment_id):

    if action == 'new':
        # new comment
        if request.method == 'POST':
            message = request.POST['message']
            if not message:
                raise Http404
            message = message[:Comment.MAX_LENGTH]

            if len(message) is 0:
                raise Http404

            comment = Comment()
            comment.user = request.user
            comment.message = message
            if comment_id is not '0':
                comment.parent = get_object_or_404(Comment,pk=comment_id)
            comment.save()
            
            response_dict = {
                'id' :  comment.parent.id,
                'status': 'new',
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

    raise Http404





