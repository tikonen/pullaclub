from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pullaclub.members.views',
    (r'^$', 'index'),
    (r'^apply/$', 'apply'),
    (r'^finance/$', 'finance'),
    (r'^profile/(?P<action>\w+)/(?P<username>\w+)/$', 'profile'),
    (r'^comment/(?P<action>\w+)/(?P<comment_id>\w+)/$', 'comment'),
    (r'^topic/(?P<action>\w+)/$', 'topic'),
    #(r'^xxx/(?P<arg>\w+)/$', 'xxx'),
    (r'^logout/$', 'logoutuser'),
)
