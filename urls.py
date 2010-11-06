from django.conf.urls.defaults import *
from home.views import *
from accounts.views import *
from accounts.forms import ProfileForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^/', include('foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', home),
    (r'^home/browse_files', browse_files),
    
    (r'^home/download/(?P<groupname>\w+)/(?P<filename>.*)$', download),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
    #(r'^accounts/', include('accounts.urls')),
    (r'^profiles/', include('profiles.urls')),
)
