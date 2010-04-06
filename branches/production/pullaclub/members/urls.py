from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pullaclub.members.views',
    (r'^$', 'index', { 'page' : '1' }),
    (r'^(?P<page>\d+)/$', 'index' ),
    (r'^apply/$', 'apply'),
    (r'^finance/$', 'finance'),
    (r'^latest/(?P<latestid>\d+)/$', 'latest'),
    (r'^profile/(?P<userid>\d+)/$', 'profile'),
    (r'^comment/iframe/$', 'iframe'),
    (r'^comment/(?P<action>\w+)/(?P<comment_id>\w+)/$', 'comment'),
    (r'^vote/(?P<comment_id>\w+)/$', 'vote'),
    (r'^topic/(?P<action>\w+)/$', 'topic'),
    (r'^logout/$', 'logoutuser'),
)

urlpatterns += patterns(
    'pullaclub.members.api',
    (r'^api/comment/(?P<action>\w+)/(?P<comment_id>\w+)/$', 'api_comment'),
    )
