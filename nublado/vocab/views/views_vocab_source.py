from django.apps import apps
from django.views.generic import (
    ListView, TemplateView
)

from core.views import ObjectSessionMixin

from .views_mixins import (
    VocabEntryMixin, VocabSourceEntrySearchMixin, VocabSourceMixin,
    VocabSourceSearchMixin, VocabSourceSessionMixin
)
from ..models import VocabContext

APP_NAME = apps.get_app_config('vocab').name


class VocabSourceDashboardView(
    VocabSourceMixin, VocabSourceSessionMixin,
    VocabSourceEntrySearchMixin, TemplateView
):
    template_name = '{0}/vocab_source_dashboard.html'.format(APP_NAME)


class VocabSourceContextsView(
    VocabSourceMixin, VocabSourceSessionMixin,
    VocabSourceEntrySearchMixin, TemplateView
):
    '''
    Gets source contexts that have associated vocab entries.
    '''
    template_name = '{0}/vocab_source_contexts.html'.format(APP_NAME)

    def get_queryset(self, **kwargs):
        qs = super(VocabSourceContextsView, self).get_queryset(**kwargs)
        qs = qs.prefetch_related(
            'vocabcontextentry_set__vocab_entry',
            'vocabcontextentry_set__vocab_entry_tags'
        )
        qs = qs.filter(
            vocab_source_id=self.vocab_source.id,
        ).distinct()
        qs = qs.order_by('-date_created')
        return qs


class VocabSourceEntryView(
    VocabEntryMixin, VocabSourceMixin,
    VocabSourceSessionMixin, TemplateView
):
    template_name = '{0}/vocab_source_entry.html'.format(APP_NAME)


class VocabSourcesView(
    ObjectSessionMixin, VocabSourceSearchMixin,
    TemplateView
):
    template_name = '{0}/vocab_sources.html'.format(APP_NAME)
