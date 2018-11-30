import dj_database_url
import django_heroku

from .base import *

PROJECT_DOMAIN = "https://cfsnublado.herokuapp.com"

DEBUG = False

ALLOWED_HOSTS = ['*']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config()
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
USERS_USE_GRAVATAR = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

django_heroku.settings(locals())
