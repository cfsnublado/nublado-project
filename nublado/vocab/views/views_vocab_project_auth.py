from collections import defaultdict

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    CreateView, TemplateView
)

from core.views import (
    AjaxFormMixin, UserstampMixin
)
from ..forms import VocabProjectCreateForm
from ..models import VocabProject, VocabSource
from ..views.views_mixins import (
    VocabProjectMixin, VocabSourceSearchMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabProjectDashboardView(
    LoginRequiredMixin, VocabProjectMixin, TemplateView
):
    template_name = '{0}/auth/vocab_project_dashboard.html'.format(APP_NAME)


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


class VocabProjectSourcesView(
    LoginRequiredMixin, VocabProjectMixin, VocabSourceSearchMixin,
    TemplateView
):
    template_name = '{0}/auth/vocab_project_sources.html'.format(APP_NAME)

    def get_queryset(self, **kwargs):
        qs = VocabSource.objects.filter(vocab_project=self.vocab_project).order_by('name')
        qs = qs.select_related('creator')
        return qs

    def get_context_data(self, **kwargs):
        context = super(VocabProjectSourcesView, self).get_context_data(**kwargs)
        vocab_sources = self.get_queryset().all()
        vocab_source_dict = defaultdict(list)
        for vocab_source in vocab_sources:
            vocab_source_dict[vocab_source.source_type].append(vocab_source)
        context['vocab_sources'] = dict(vocab_source_dict)
        return context
