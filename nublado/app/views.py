from django.views.generic import TemplateView, View

from core.views import AjaxSessionMixin


class AppSessionView(AjaxSessionMixin, View):
    pass


class HomeView(TemplateView):
    template_name = "home.html"
