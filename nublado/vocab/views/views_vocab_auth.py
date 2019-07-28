from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from core.views import ObjectSessionMixin

APP_NAME = apps.get_app_config('vocab').name


class VocabUserDashboardView(
    LoginRequiredMixin,
    ObjectSessionMixin, TemplateView
):
    template_name = '{0}/auth/vocab_user_dashboard.html'.format(APP_NAME)

    def get_context_data(self, **kwargs):
        context = super(VocabUserDashboardView, self).get_context_data(**kwargs)

        return context
