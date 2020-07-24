from django.apps import apps
from django.views.generic import (
    TemplateView
)

from core.views import ObjectSessionMixin

from ..models import VocabContextEntry
from .views_mixins import (
    VocabEntryMixin, VocabSourceEntrySearchMixin, VocabSourceMixin,
    VocabSourceSearchMixin, VocabSourceSessionMixin
)

APP_NAME = apps.get_app_config("vocab").name


class VocabSourceDashboardView(
    VocabSourceMixin, VocabSourceSessionMixin,
    VocabSourceEntrySearchMixin, TemplateView
):
    template_name = "{0}/vocab_source_dashboard.html".format(APP_NAME)


class VocabSourceEntriesView(
    VocabSourceMixin, VocabSourceSessionMixin,
    VocabSourceEntrySearchMixin, TemplateView
):
    template_name = "{0}/vocab_source_entries.html".format(APP_NAME)

    def get_context_data(self, **kwargs):
        context = super(VocabSourceEntriesView, self).get_context_data(**kwargs)
        max_language = VocabContextEntry.objects.source_entry_language_max(
            self.vocab_source.id
        )
        if not max_language:
            max_language = "en"
        context["max_language"] = max_language
        return context


class VocabSourceContextsView(
    VocabSourceMixin, VocabSourceSessionMixin,
    VocabSourceEntrySearchMixin, TemplateView
):
    """
    Gets source contexts that have associated vocab entries.
    """
    template_name = "{0}/vocab_source_contexts.html".format(APP_NAME)

    def get_queryset(self, **kwargs):
        qs = super(VocabSourceContextsView, self).get_queryset(**kwargs)
        qs = qs.prefetch_related(
            "vocabcontextentry_set__vocab_entry",
            "vocabcontextentry_set__vocab_entry_tags"
        )
        qs = qs.filter(
            vocab_source_id=self.vocab_source.id,
        ).distinct()
        qs = qs.order_by("-date_created")
        return qs


class VocabSourceContextsAudiosView(
    VocabSourceContextsView
):
    template_name = "{0}/vocab_source_contexts_audios.html".format(APP_NAME)


class VocabSourceEntryView(
    VocabEntryMixin, VocabSourceMixin,
    VocabSourceSessionMixin, TemplateView
):
    template_name = "{0}/vocab_source_entry.html".format(APP_NAME)


class VocabSourcesView(
    ObjectSessionMixin, VocabSourceSearchMixin,
    TemplateView
):
    template_name = "{0}/vocab_sources.html".format(APP_NAME)
