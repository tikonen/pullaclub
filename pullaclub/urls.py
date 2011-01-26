from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.syndication.views import feed

from pullaclub.members.api import login_required_basicauth
from pullaclub.members.feeds import LatestComments

# Enable admin gui
from django.contrib import admin
admin.autodiscover()

# RSS feeds
feeds = {
    'latest': LatestComments,
}


urlpatterns = patterns(
    '',
    (r'^members/', include('pullaclub.members.urls')),

    (r'^admin/', include(admin.site.urls)),

    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'members/login.html'}),
    (r'^changepassword/$', 'django.contrib.auth.views.password_change', 
     { 'template_name': 'members/password_change_form.html'}),
    (r'^changeok/$', 'django.contrib.auth.views.password_change_done',
     { 'template_name': 'members/password_change_done.html'}),

    (r'^feeds/(?P<url>.*)/$', login_required_basicauth(feed,realm="PullaClub Feed"), {'feed_dict': feeds}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.PULLACLUB_DEV:
    urlpatterns += patterns(
        '',
        # this should be deleted from production version
        (r'^(?P<path>[^\.]*\..*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT }),
        )
