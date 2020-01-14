from django.views.generic import TemplateView, View

from core.views import AjaxSessionMixin, ObjectSessionMixin
from vocab.utils import get_random_vocab_entry


class AppSessionView(AjaxSessionMixin, View):
    pass


class HomeView(ObjectSessionMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["random_vocab_entry"] = get_random_vocab_entry()

        return context
