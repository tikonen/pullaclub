from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pullaclub.members.views',
    (r'^$', 'index'),
    (r'^apply/$', 'apply'),
#    (r'^comment/$', 'newcomment'),
    #(r'^xxx/(?P<arg>\w+)/$', 'xxx'),
    (r'^logout/$', 'logoutuser'),
)
