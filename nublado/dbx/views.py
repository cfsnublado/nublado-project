from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from core.views import (
    ObjectSessionMixin
)

APP_NAME = apps.get_app_config('dbx').name


class DbxView(
    LoginRequiredMixin, ObjectSessionMixin, TemplateView
):
    template_name = '{0}/dbx.html'.format(APP_NAME)
