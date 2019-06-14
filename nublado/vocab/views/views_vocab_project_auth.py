from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView,
    UpdateView
)

from core.views import (
    AjaxDeleteMixin, AjaxFormMixin, MessageMixin,
    UserstampMixin
)
from ..forms import VocabProjectCreateForm, VocabProjectUpdateForm
from ..models import VocabProject, VocabSource
from ..views.views_mixins import (
    VocabProjectMixin, VocabProjectSessionMixin,
)

APP_NAME = apps.get_app_config('vocab').name


class VocabProjectCreateView(
    LoginRequiredMixin, AjaxFormMixin,
    UserstampMixin, CreateView
):
    model = VocabProject
    form_class = VocabProjectCreateForm
    template_name = '{0}/auth/vocab_project_create.html'.format(APP_NAME)

    def get_form_kwargs(self):
        kwargs = super(VocabProjectCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse(
            'vocab:vocab_project_dashboard',
            kwargs={
                'vocab_project_pk': self.object.id,
                'vocab_project_slug': self.object.slug
            }
        )


class VocabProjectUpdateView(
    LoginRequiredMixin, VocabProjectMixin,
    VocabProjectSessionMixin,
    MessageMixin, UpdateView
):
    model = VocabSource
    form_class = VocabProjectUpdateForm
    template_name = '{0}/auth/vocab_project_update.html'.format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_project

    def get_success_url(self):
        return reverse(
            'vocab:vocab_project_dashboard',
            kwargs={
                'vocab_project_pk': self.vocab_project.id,
                'vocab_project_slug': self.vocab_project.slug
            }
        )


class VocabProjectDeleteView(
    LoginRequiredMixin, VocabProjectMixin,
    VocabProjectSessionMixin,
    AjaxDeleteMixin, DeleteView
):
    model = VocabSource
    template_name = '{0}/auth/vocab_project_delete_confirm.html'.format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_project

    def get_success_url(self):
        return reverse('vocab:vocab_user_dashboard')
