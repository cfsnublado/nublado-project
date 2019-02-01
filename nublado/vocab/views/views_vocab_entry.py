from django.apps import apps
from django.views.generic import TemplateView

from core.views import ObjectSessionMixin
from .views_mixins import (
    VocabEntryMixin, VocabEntrySearchMixin,
    VocabEntrySessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabEntryDashboardView(
    VocabEntryMixin, VocabEntrySessionMixin,
    TemplateView
):
    template_name = '{0}/vocab_entry_dashboard.html'.format(APP_NAME)


class VocabEntriesView(
    VocabEntrySearchMixin, ObjectSessionMixin,
    TemplateView
):
    search_term = None
    search_language = None
    template_name = '{0}/vocab_entries.html'.format(APP_NAME)
