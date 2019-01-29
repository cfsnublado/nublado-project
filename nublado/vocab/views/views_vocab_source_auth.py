from collections import defaultdict

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView,
    UpdateView, View
)

from core.views import (
    AjaxDeleteMixin, MessageMixin,
    JsonAttachmentMixin
)
from ..forms import VocabSourceCreateForm, VocabSourceUpdateForm
from ..models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabSource
)
from ..utils import export_vocab_source
from .views_mixins import (
    VocabEntrySearchMixin, VocabProjectMixin, VocabSourceMixin,
    VocabSourcePermissionMixin, VocabSourceSessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabSourceExportJsonView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    JsonAttachmentMixin, View
):
    content_type = 'application/json'
    json_indent = 4

    def get_file_content(self):
        vocab_source = get_object_or_404(
            VocabSource.objects.prefetch_related(
                'creator',
                'vocab_contexts__vocabcontextentry_set__vocab_entry'
            ),
            id=self.kwargs['vocab_source_pk']
        )
        self.filename = '{0}.json'.format(vocab_source.slug)
        data = export_vocab_source(self.request, vocab_source)
        return data


class VocabSourceDashboardView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    TemplateView
):
    template_name = '{0}/auth/vocab_source_dashboard.html'.format(APP_NAME)

    def get_context_data(self, **kwargs):
        context = super(VocabSourceDashboardView, self).get_context_data(**kwargs)
        return context


class VocabSourceEntriesView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    VocabEntrySearchMixin, TemplateView
):
    '''
    Return vocab entries used in a specific source.
    '''
    template_name = '{0}/auth/vocab_source_entries.html'.format(APP_NAME)
    search_redirect_url = 'vocab:vocab_entry_dashboard_auth'

    def search_success(self, **kwargs):
        return redirect(
            'vocab:vocab_source_entry_contexts',
            vocab_source_pk=self.vocab_source.id,
            vocab_source_slug=self.vocab_source.slug,
            vocab_entry_language=self.vocab_entry.language,
            vocab_entry_slug=self.vocab_entry.slug
        )

    def get_queryset(self, **kwargs):
        qs = VocabContextEntry.objects.select_related('vocab_context', 'vocab_entry')
        qs = qs.filter(vocab_context__vocab_source_id=self.vocab_source.id)
        qs = qs.order_by('vocab_entry__entry').distinct()
        qs = qs.values(
            'vocab_entry_id',
            language=Lower('vocab_entry__language'),
            slug=Lower('vocab_entry__slug'),
            entry=Lower('vocab_entry__entry')
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super(VocabSourceEntriesView, self).get_context_data(**kwargs)
        vocab_entries = self.get_queryset().all()
        vocab_entry_dict = defaultdict(list)
        for vocab_entry in vocab_entries:
            vocab_entry_dict[vocab_entry['language']].append(vocab_entry)
        context['vocab_entries'] = dict(vocab_entry_dict)
        return context


class VocabSourceContextsView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    VocabEntrySearchMixin, ListView
):
    '''
    Gets source contexts that have associated vocab entries.
    '''
    model = VocabContext
    context_object_name = 'vocab_contexts'
    template_name = '{0}/auth/vocab_source_contexts.html'.format(APP_NAME)
    paginate_by = 10

    def search_success(self, **kwargs):
        return redirect(
            'vocab:vocab_source_entry_contexts',
            vocab_source_pk=self.vocab_source.id,
            vocab_source_slug=self.vocab_source.slug,
            vocab_entry_language=self.vocab_entry.language,
            vocab_entry_slug=self.vocab_entry.slug
        )

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


class VocabSourceEntryContextsView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    ListView
):
    '''
    Returns a list of contexts tagged with a specific entry within a source.
    '''
    model = VocabContextEntry
    context_object_name = 'vocab_entry_contexts'
    template_name = '{0}/auth/vocab_source_entry_contexts.html'.format(APP_NAME)
    pagination = 10

    def dispatch(self, request, *args, **kwargs):
        self.vocab_entry = get_object_or_404(
            VocabEntry,
            language=kwargs['vocab_entry_language'],
            slug=kwargs['vocab_entry_slug']
        )
        return super(VocabSourceEntryContextsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        qs = super(VocabSourceEntryContextsView, self).get_queryset(**kwargs)
        qs = qs.select_related('vocab_context__vocab_source', 'vocab_entry')
        qs = qs.prefetch_related('vocab_context__vocab_entries', 'vocab_entry_tags')
        qs = qs.filter(
            vocab_context__vocab_source_id=self.vocab_source.id,
            vocab_entry_id=self.vocab_entry.id
        )
        qs = qs.order_by('-date_created')
        return qs

    def get_context_data(self, **kwargs):
        context = super(VocabSourceEntryContextsView, self).get_context_data(**kwargs)
        context['vocab_entry'] = self.vocab_entry
        return context


class VocabSourceCreateView(
    LoginRequiredMixin, VocabProjectMixin,
    MessageMixin, CreateView
):
    model = VocabSource
    form_class = VocabSourceCreateForm
    template_name = '{0}/auth/vocab_source_create.html'.format(APP_NAME)

    def get_form_kwargs(self):
        kwargs = super(VocabSourceCreateView, self).get_form_kwargs()
        kwargs['vocab_project'] = self.vocab_project
        kwargs['creator'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse(
            'vocab:vocab_source_dashboard',
            kwargs={
                'vocab_source_pk': self.object.id,
                'vocab_source_slug': self.object.slug
            }
        )


class VocabSourceUpdateView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    MessageMixin, UpdateView
):
    model = VocabSource
    form_class = VocabSourceUpdateForm
    template_name = '{0}/auth/vocab_source_update.html'.format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_source

    def get_success_url(self):
        return reverse(
            'vocab:vocab_source_dashboard',
            kwargs={
                'vocab_source_pk': self.object.id,
                'vocab_source_slug': self.object.slug
            }
        )


class VocabSourceDeleteView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    AjaxDeleteMixin, DeleteView
):
    model = VocabSource
    template_name = '{0}/auth/vocab_source_delete_confirm.html'.format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_source

    def get_success_url(self):
        return reverse(
            'vocab:vocab_project_sources',
            kwargs={
                'vocab_project_pk': self.vocab_project.id,
                'vocab_project_slug': self.vocab_project.slug
            }
        )
