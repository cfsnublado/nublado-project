from .base import *

PROJECT_DOMAIN = "http://127.0.0.1:8000"

DEBUG = True

# ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["debug_toolbar", ]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware", ]
DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = [
    "127.0.0.1",
    "::1"
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["DATABASE_NAME"],
        "USER": os.environ["DATABASE_USER"],
        "PASSWORD": os.environ["DATABASE_PWD"],
        "HOST": "localhost",
        "PORT": "",
    }
}

USERS_USE_GRAVATAR = True
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "/home/cfs/tmp/email-messages/"
