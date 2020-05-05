from appconf import AppConf

from django.conf import settings


class ProfileConf(AppConf):
    URL_PREFIX = 'profile'
    IMAGE_DEFAULT_SIZE = 100
    IMAGE_MAX_SIZE = 1024 * 1024
    IMAGE_DEFAULT_URL = 'https://i.imgur.com/m0cVFB2.jpg'
    USE_GRAVATAR = False
    GRAVATAR_BASE_URL = 'https://www.gravatar.com/avatar/'
    GRAVATAR_CHANGE_URL = 'https://www.gravatar.com'
    GRAVATAR_DEFAULT = 'identicon'
