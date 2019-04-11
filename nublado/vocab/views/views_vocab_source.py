from django.apps import apps
from django.views.generic import (
    TemplateView
)

from .views_mixins import (
    VocabEntryMixin, VocabEntrySearchMixin, VocabSourceMixin, VocabSourceSessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabSourceDashboardView(
    VocabSourceMixin, VocabSourceSessionMixin,
    VocabEntrySearchMixin, TemplateView
):
    template_name = '{0}/vocab_source_dashboard.html'.format(APP_NAME)


class VocabSourceEntryView(
    VocabSourceMixin,
    VocabSourceSessionMixin, TemplateView
):
    template_name = '{0}/vocab_source_entry.html'.format(APP_NAME)
