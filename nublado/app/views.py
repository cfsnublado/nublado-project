from django.views.generic import TemplateView, View

from core.views import AjaxSessionMixin, ObjectSessionMixin


class AppSessionView(AjaxSessionMixin, View):
    pass


class HomeView(ObjectSessionMixin, TemplateView):
    template_name = "home.html"
