import os
import sys

sys.path.append('/home/subsea/application')

os.environ['PYTHON_EGG_CACHE'] = '/home/subsea/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()