import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


# Get key env values from the virtual environment.
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the {} environment variable.'.format(var_name)
        raise ImproperlyConfigured(error_msg)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR_NAME = 'nublado'

sys.path.append(os.path.join(BASE_DIR, PROJECT_DIR_NAME))

PROJECT_ROOT = BASE_DIR / PROJECT_DIR_NAME
PROJECT_NAME = 'Nublado'
PROJECT_HOME_URL = 'app:home'
PROJECT_AUTH_HOME_URL = 'app:home'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')

# Custom User model
AUTH_USER_MODEL = 'users.User'

# Authentication defaults
LOGIN_URL = 'security:login'
LOGIN_REDIRECT_URL = PROJECT_AUTH_HOME_URL
LOGOUT_REDIRECT_URL = PROJECT_HOME_URL

MEDIA_ROOT = PROJECT_ROOT / 'media'
MEDIA_URL = '/media/'

TMP_DIR = MEDIA_ROOT / 'tmp'

STATIC_ROOT = PROJECT_ROOT / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = [PROJECT_ROOT / 'static']

ALLOWED_HOSTS = []

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'app',
    'users',
    'core',
    'security',
    'vocab',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'widget_tweaks',
    'betterforms',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Internationalization and Localization
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
)
LANGUAGES_DICT = dict(LANGUAGES)

LOCALE_PATHS = (
    PROJECT_ROOT / 'app' / 'locale',
)

TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_ROOT / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.global_settings'
            ],
        },
    },
]
