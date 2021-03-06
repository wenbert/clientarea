# Django settings for subsea project.
import os.path
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'subsea',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'root',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Europe/Oslo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b+hq#s_w_7k8al$n16#q7+28gf2$tf6log&mb3_8899p9dd$+*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'registration',
    'profiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'home',
    'accounts',
    'message',
    'uploadify',
)

#---------------------------------------
#OTHER SETTINGS
#---------------------------------------
AUTH_PROFILE_MODULE = 'accounts.UserProfile'
PAGE_ITEMS = 10
LOGIN_URL = "/accounts/login"
LOGIN_REDIRECT_URL = "/"
#LOGOUT_URL = "/business/browse"
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(os.path.dirname(__file__), '_app_messages')

"""
Logo URL and Text
"""
LOGO_URL = "http://client.npo-inc.com/images/subsea.png"
LOGO_TEXT = "Subsea International"

"""
Images, CSS, other stuff.
"""
IMAGES_DOC_ROOT = os.path.join(os.path.dirname(__file__), '/home/subsea/public_html/images')
JS_DOC_ROOT = os.path.join(os.path.dirname(__file__), '/home/subsea/public_html/js')
CSS_DOC_ROOT = os.path.join(os.path.dirname(__file__), '/home/subsea/public_html/css')
STATIC_DOC_ROOT = os.path.join(os.path.dirname(__file__), '/home/subsea/public_html/static')

"""
this is where all the files will be stored!
also check the /etc/apache2/sites-available/client.npo-inc.com 
for the Xsendfile setting
"""
APPLICATION_STORAGE = '/home/subsea/clientarea/storage'

#README_FILE will be read by the app to display information for directories
README_FILE = 'README'

#README_FILE_EXT will be read by the app to display information for files
README_FILE_EXT = '.README'

#TIME_FORMAT used to format the time displayed when browsing the files
TIME_FORMAT = '%a, %d %b %Y %H:%M:%S'


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = './email_tmp' # change this to a proper location