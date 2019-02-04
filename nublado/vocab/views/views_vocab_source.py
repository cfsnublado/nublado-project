from django.apps import apps
from django.views.generic import (
    TemplateView
)

from .views_mixins import (
    VocabSourceMixin, VocabSourceSessionMixin
)

APP_NAME = apps.get_app_config('vocab').name


class VocabSourceDashboardView(
    VocabSourceMixin, VocabSourceSessionMixin,
    TemplateView
):
    template_name = '{0}/vocab_source_dashboard.html'.format(APP_NAME)
