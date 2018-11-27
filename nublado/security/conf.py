from appconf import AppConf

from django.conf import settings


class SecurityConf(AppConf):
    URL_PREFIX = 'accounts'
