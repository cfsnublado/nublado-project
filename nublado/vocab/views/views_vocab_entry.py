from django.apps import apps
from django.views.generic import TemplateView

from core.views import ObjectSessionMixin
from ..models import VocabContextEntry
from .views_mixins import VocabEntrySearchMixin

APP_NAME = apps.get_app_config('vocab').name


class VocabEntrySearchView(
    VocabEntrySearchMixin, ObjectSessionMixin, TemplateView
):
    search_term = None
    search_language = None
    template_name = '{0}/vocab_search.html'.format(APP_NAME)
    vocab_entry_contexts = None

    def get_vocab_entry_contexts(self, **kwargs):
        qs = VocabContextEntry.objects.filter(vocab_entry_id=self.vocab_entry.id)
        qs = qs.select_related('vocab_context__vocab_source', 'vocab_entry')
        qs = qs.prefetch_related('vocab_context__vocab_entries', 'vocab_entry_tags')
        qs = qs.order_by('-date_created')
        return qs

    def search_success(self, *args, **kwargs):
        self.vocab_entry_contexts = self.get_vocab_entry_contexts()
        return self.get(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VocabEntrySearchView, self).get_context_data(**kwargs)
        context['vocab_entry_contexts'] = self.vocab_entry_contexts
        return context
