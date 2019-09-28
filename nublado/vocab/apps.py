from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VocabConfig(AppConfig):
    name = "vocab"
    verbose_name = _("label_vocab_config")

    def ready(self):
        from . import signals
