# Django settings for pullaclub project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PULLACLUB_DEV = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'pullaclub'
DATABASE_USER = 'pullaclub'
DATABASE_PASSWORD = 'pullaclub'
DATABASE_HOST = 'mysql.pullaclub.com'
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

if PULLACLUB_DEV:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = '/home/teemu/pulla/pullaclub/pullaclub.db'            

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/tikonen/pullaclub.com/public/media'

if PULLACLUB_DEV:
    MEDIA_ROOT = '/home/teemu/pulla/pullaclub/public'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5-v_-&k-=@i0$e^9(74m8a%6k+jw%-larw*28!an87((r9*+wv'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'pullaclub.urls'

LOGIN_URL='/login'

PULLACLUB_TEMPLATE_DIR = '/home/tikonen/pullaclub.com/templates'

if PULLACLUB_DEV:
    PULLACLUB_TEMPLATE_DIR='/home/teemu/pulla/pullaclub/templates'

TEMPLATE_DIRS = (
    PULLACLUB_TEMPLATE_DIR,
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'pullaclub.members',
)
