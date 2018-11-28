from appconf import AppConf

from django.conf import settings


class VocabConf(AppConf):
    URL_PREFIX = 'vocab'
