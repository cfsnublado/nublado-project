from django.apps import apps
from django.views.generic import (
    TemplateView
)

from core.views import ObjectSessionMixin

from .views_mixins import (
    VocabProjectMixin, VocabProjectSessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabProjectsView(
    ObjectSessionMixin, TemplateView
):
    template_name = '{0}/vocab_projects.html'.format(APP_NAME)


class VocabProjectDashboardView(
    VocabProjectMixin, VocabProjectSessionMixin,
    TemplateView
):
    template_name = '{0}/vocab_project_dashboard.html'.format(APP_NAME)
