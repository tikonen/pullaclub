import base64

from django.contrib.syndication.views import feed
from django.contrib.syndication.feeds import Feed
from django.conf import settings

from pullaclub.members.models import Comment
from pullaclub.members.api import login_required_basicauth

class LatestComments(Feed):
    title = 'PullaClub latest comments'
    link = '/members/'
    description = "Latest comments from PullaClub.com"

    def items(self):
        return Comment.objects.order_by('-datetime')[:5]

    def item_link(self,comment):
        return '/members/1#'+str(comment.id)

        
