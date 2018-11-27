from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserConfig(AppConfig):
    name = 'users'
    verbose_name = _('label_user_config')

    def ready(self):
        from . import signals
