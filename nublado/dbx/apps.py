from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DbxConfig(AppConfig):
    name = "dbx"
    verbose_name = _("label_dbx_config")

    def ready(self):
        pass
