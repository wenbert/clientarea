from django.conf.urls.defaults import *
from home.views import *
from message.views import *
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
    (r'^$', dashboard),
    (r'^home/directories', directories),
    (r'^home/forbidden', forbidden),
    (r'^home/browse_files/(?P<groupname>[-\w]+)', browse_files),    
    (r'^home/download_dir_as_zip/(?P<groupname>\w+)', download_dir_as_zip),
    (r'^home/download/(?P<groupname>\w+)/(?P<filename>.*)$', download),
    #(r'^home/save_readme/(?P<groupname>\w+)/(?P<filename>.*)$', save_readme),
    (r'^home/save_readme', save_readme),
    (r'^home/add_comment/(?P<groupname>\w+)/(?P<filename>.*)$', add_comment),
    (r'^home/download_file_as_zip/(?P<groupname>\w+)/(?P<filename>.*)$', download_file_as_zip),
    (r'^message/dashboard', allmessages),
    (r'^message/post_message/(?P<groupid>[-\w]+)', post_message),
    (r'^message/view/(?P<messageid>[-\w]+)', view),
    (r'^message/group/(?P<groupid>[-\w]+)', by_group),
    (r'^message/cat/(?P<groupid>[-\w]+)/(?P<categoryid>[-\w]+)/', by_category),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
    #(r'^accounts/', include('accounts.urls')),
    # First match /profiles/edit before django-profiles gets it so we can pass in our custom form object.
    ('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),
    (r'^profiles/', include('profiles.urls')),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.IMAGES_DOC_ROOT, 'show_indexes': True}),
        (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.JS_DOC_ROOT, 'show_indexes': True}),
        (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.CSS_DOC_ROOT, 'show_indexes': True}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
    )