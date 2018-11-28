from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .views_mixins import VocabSessionMixin
from ..models import VocabProject

APP_NAME = apps.get_app_config('vocab').name


class VocabUserDashboardView(
    LoginRequiredMixin,
    VocabSessionMixin, TemplateView
):
    template_name = '{0}/auth/vocab_user_dashboard.html'.format(APP_NAME)

    def get_user_projects(self):
        projects = VocabProject.objects.filter(owner=self.request.user)
        return projects

    def get_context_data(self, **kwargs):
        context = super(VocabUserDashboardView, self).get_context_data(**kwargs)
        context['vocab_projects'] = self.get_user_projects()
        return context
