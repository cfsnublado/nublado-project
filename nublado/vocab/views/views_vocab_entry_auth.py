from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, UpdateView
)

from core.views import (
    AjaxDeleteMixin,
    MessageMixin, ObjectSessionMixin,
    UserstampMixin
)
from ..forms import VocabEntryCreateForm, VocabEntryUpdateForm
from ..models import VocabEntry
from .views_mixins import (
    VocabEntryMixin,
    VocabEntryPermissionMixin, VocabEntrySessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


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
