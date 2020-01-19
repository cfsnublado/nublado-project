from appconf import AppConf

from django.conf import settings


class AppdocsConf(AppConf):
    URL_PREFIX = "docs"
