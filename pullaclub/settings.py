# Django settings for pullaclub project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG
PULLACLUB_DEV = False

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
    DATABASE_NAME = '/home/teemu/pulla/trunk/sqlite.db'            

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
MEDIA_ROOT = '/home/pullaclub/pullaclub.com/public/'

DEFAULT_IMAGE = 'default.jpg'
PHOTO_UPLOAD_DIR = 'photos/%y%m%d'
COMMENT_IMAGE_UPLOAD_DIR = 'photos/upload/%y%m%d'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/'

if PULLACLUB_DEV:
    MEDIA_ROOT = '/home/teemu/pulla/trunk/public'


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
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
)

ROOT_URLCONF = 'pullaclub.urls'

LOGIN_URL='/login'
AUTH_PROFILE_MODULE = 'members.UserProfile'

PULLACLUB_TEMPLATE_DIR = '/home/pullaclub/pullaclub.com/templates'

if PULLACLUB_DEV:
    PULLACLUB_TEMPLATE_DIR='/home/teemu/pulla/trunk/templates'

TEMPLATE_DIRS = (
    PULLACLUB_TEMPLATE_DIR,
)

DEFAULT_USER_DESCRIPTION = 'Pikkupulla'

# settings for MMS import
POP_HOST = 'mail.pullaclub.com'
POP_USERNAME = 'mms@pullaclub.com'
POP_PASSWORD = 'pullakausi'
MMS_USER = 'mms'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'pullaclub.members',
)
