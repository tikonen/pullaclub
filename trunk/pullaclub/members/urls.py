from django.conf.urls.defaults import *

urlpatterns = patterns(
    'members.views',
    (r'^$', 'index'),
    (r'^apply/$', 'apply'),
#    (r'^comment/$', 'newcomment'),
    #(r'^xxx/(?P<arg>\w+)/$', 'xxx'),
    (r'^logout/$', 'logoutuser'),
)
