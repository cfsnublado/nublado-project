from collections import defaultdict

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView
)

from ..models import VocabSource
from ..views.views_mixins import (
    VocabProjectMixin, VocabSourceSearchMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabProjectDashboardView(
    LoginRequiredMixin, VocabProjectMixin, TemplateView
):
    template_name = '{0}/auth/vocab_project_dashboard.html'.format(APP_NAME)


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
