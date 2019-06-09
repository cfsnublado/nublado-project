from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView,
    UpdateView
)

from core.views import (
    AjaxDeleteMixin,
    MessageMixin, ObjectSessionMixin,
    UserstampMixin
)
from ..conf import settings
from ..forms import VocabEntryCreateForm, VocabEntryUpdateForm
from ..models import VocabContextEntry, VocabEntry
from .views_mixins import (
    VocabEntryMixin, VocabEntrySearchMixin,
    VocabEntryPermissionMixin, VocabEntrySessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabEntryView(
    LoginRequiredMixin, VocabEntryMixin,
    VocabEntryPermissionMixin, VocabEntrySessionMixin,
    TemplateView
):
    search_term = None
    search_language = None
    template_name = '{0}/auth/vocab_entry.html'.format(APP_NAME)

    def get_context_data(self, **kwargs):
        context = super(VocabEntryView, self).get_context_data(**kwargs)
        context['search_term'] = self.search_term
        context['search_language'] = self.search_language
        return context


class VocabEntriesView(
    LoginRequiredMixin, VocabEntrySearchMixin,
    ObjectSessionMixin, ListView
):
    model = VocabEntry
    context_object_name = 'vocab_entries'
    template_name = '{0}/auth/vocab_entries.html'.format(APP_NAME)
    paginate_by = 50
    language = None
    search_redirect_url = 'vocab:vocab_entry_auth'

    def get(self, request, *args, **kwargs):
        self.language = self.request.GET.get('language', settings.LANGUAGE_CODE)
        if self.language and self.language not in settings.LANGUAGES_DICT:
            self.language = settings.LANGUAGE_CODE
        return super(VocabEntriesView, self).get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        qs = super(VocabEntriesView, self).get_queryset(**kwargs)
        qs = qs.filter(
            language=self.language
        )
        qs = qs.order_by('entry')
        return qs

    def get_context_data(self, **kwargs):
        context = super(VocabEntriesView, self).get_context_data(**kwargs)
        context['language'] = self.language
        context['language_name'] = settings.LANGUAGES_DICT[self.language]
        return context


class VocabEntryContextsView(
    LoginRequiredMixin, VocabEntryMixin,
    VocabEntryPermissionMixin, VocabEntrySessionMixin,
    ListView
):
    '''
    Returns contexts containing a specified tagged vocab entry.
    '''
    model = VocabContextEntry
    context_object_name = 'vocab_entry_contexts'
    template_name = '{0}/auth/vocab_entry_contexts.html'.format(APP_NAME)
    paginate_by = 10

    def get_queryset(self, **kwargs):
        qs = super(VocabEntryContextsView, self).get_queryset(**kwargs)
        qs = qs.select_related('vocab_context__vocab_source', 'vocab_entry')
        qs = qs.prefetch_related('vocab_context__vocab_entries', 'vocab_entry_tags')
        qs = qs.filter(vocab_entry_id=self.vocab_entry.id)
        qs = qs.order_by('-date_created')
        return qs


class VocabEntryCreateView(
    LoginRequiredMixin, ObjectSessionMixin,
    UserstampMixin, CreateView
):
    model = VocabEntry
    form_class = VocabEntryCreateForm
    template_name = '{0}/auth/vocab_entry_create.html'.format(APP_NAME)

    def get_success_url(self):
        return reverse(
            'vocab:vocab_entry',
            kwargs={
                'vocab_entry_language': self.object.language,
                'vocab_entry_slug': self.object.slug
            }
        )


class VocabEntryUpdateView (
    LoginRequiredMixin, UserstampMixin, MessageMixin,
    VocabEntryMixin, VocabEntryPermissionMixin,
    VocabEntrySessionMixin, UpdateView
):
    model = VocabEntry
    form_class = VocabEntryUpdateForm
    template_name = '{0}/auth/vocab_entry_update.html'.format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_entry

    def get_success_url(self):
        return reverse(
            'vocab:vocab_entry',
            kwargs={
                'vocab_entry_language': self.vocab_entry.language,
                'vocab_entry_slug': self.vocab_entry.slug
            }
        )


class VocabEntryDeleteView(
    LoginRequiredMixin, VocabEntryMixin,
    VocabEntryPermissionMixin, VocabEntrySessionMixin,
    AjaxDeleteMixin, DeleteView
):
    model = VocabEntry
    template_name = '{0}/auth/vocab_entry_delete_confirm.html'.format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_entry

    def get_success_url(self):
        return reverse('vocab:vocab_entries')
