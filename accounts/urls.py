from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login, logout, password_change, password_reset
from registration.views import register, activate
from registration.forms import *
#from pley.accounts.forms import CustomRegistrationForm

urlpatterns = patterns('',
                url(r'^register/complete/$',
                   direct_to_template,
                   {'template': 'registration/registration_complete.html'},
                   name='registration_complete'),
                url(r'^register/closed/$',
                   direct_to_template,
                   {'template': 'registration/registration_closed.html'},
                   name='registration_disallowed'),
                url(r'^password/change/$',
                   password_change),
                #(r'^', include('registration.backends.default.urls')),
                (r'', include('registration.backends.default.urls')),
            )
