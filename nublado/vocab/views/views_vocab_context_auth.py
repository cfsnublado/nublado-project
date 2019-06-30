import json

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView
)

from core.views import AjaxDeleteMixin
from ..forms import VocabContextCreateForm
from ..models import (VocabContextEntry, VocabContext)
from .views_mixins import VocabSourcePermissionMixin, VocabSourceMixin

APP_NAME = apps.get_app_config('vocab').name


# VocabContext
class VocabContextCreateView(
    LoginRequiredMixin,
    VocabSourceMixin, CreateView
):
    model = VocabContext
    form_class = VocabContextCreateForm
    template_name = '{0}/auth/vocab_context_create.html'.format(APP_NAME)

    def get_form_kwargs(self):
        kwargs = super(VocabContextCreateView, self).get_form_kwargs()
        kwargs['vocab_source'] = self.vocab_source
        return kwargs

    def get_success_url(self):
        return reverse('vocab:vocab_context_tag', kwargs={'vocab_context_pk': self.object.id})


class VocabContextTagView(
    VocabSourceMixin, DetailView
):
    model = VocabContext
    pk_url_kwarg = 'vocab_context_pk'
    context_object_name = 'vocab_context'
    template_name = '{0}/auth/vocab_context_tag.html'.format(APP_NAME)

    def get_queryset(self):
        qs = super(VocabContextTagView, self).get_queryset()
        qs = qs.select_related('vocab_source')
        qs = qs.prefetch_related(
            'vocabcontextentry_set__vocab_entry',
            'vocabcontextentry_set__vocab_entry_tags'
        )
        qs = qs.order_by('-date_created')
        return qs

    def get_context_data(self, **kwargs):
        context = super(VocabContextTagView, self).get_context_data(**kwargs)
        vocab_entry_tags = self.object.get_entries_and_tags()
        context['vocab_entry_tags'] = json.dumps(vocab_entry_tags)
        return context


class VocabContextEntryTagView(
    LoginRequiredMixin, DetailView
):
    model = VocabContextEntry
    pk_url_kwarg = 'vocab_context_entry_pk'
    context_object_name = 'vocab_context_entry'
    template_name = '{0}/auth/vocab_context_entry_tag.html'.format(APP_NAME)

    def get_queryset(self, **kwargs):
        qs = super(VocabContextEntryTagView, self).get_queryset(**kwargs)
        qs = qs.select_related('vocab_entry', 'vocab_context')
        qs = qs.prefetch_related('vocab_entry_tags')
        return qs
