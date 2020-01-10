from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, TemplateView,
    UpdateView, View
)

from core.views import (
    AjaxDeleteMixin, JsonAttachmentMixin,
    MessageMixin, ObjectSessionMixin
)
from ..forms import VocabSourceCreateForm, VocabSourceUpdateForm
from ..models import (
    VocabSource
)
from ..utils import export_vocab_source
from .views_mixins import (
    VocabSourceMixin, VocabSourcePermissionMixin,
    VocabSourceSearchMixin, VocabSourceSessionMixin
)

APP_NAME = apps.get_app_config("vocab").name


class VocabSourcesView(
    LoginRequiredMixin, ObjectSessionMixin,
    VocabSourceSearchMixin, TemplateView
):
    template_name = "{0}/auth/vocab_sources.html".format(APP_NAME)


class VocabSourceCreateView(
    LoginRequiredMixin, ObjectSessionMixin,
    MessageMixin, CreateView
):
    model = VocabSource
    form_class = VocabSourceCreateForm
    template_name = "{0}/auth/vocab_source_create.html".format(APP_NAME)

    def get_form_kwargs(self):
        kwargs = super(VocabSourceCreateView, self).get_form_kwargs()
        kwargs["creator"] = self.request.user

        return kwargs

    def get_success_url(self):
        return reverse(
            "vocab:vocab_source_dashboard",
            kwargs={
                "vocab_source_pk": self.object.id,
                "vocab_source_slug": self.object.slug
            }
        )


class VocabSourceUpdateView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    MessageMixin, UpdateView
):
    model = VocabSource
    form_class = VocabSourceUpdateForm
    template_name = "{0}/auth/vocab_source_update.html".format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_source

    def get_success_url(self):
        return reverse(
            "vocab:vocab_source_dashboard",
            kwargs={
                "vocab_source_pk": self.object.id,
                "vocab_source_slug": self.object.slug
            }
        )


class VocabSourceDeleteView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    AjaxDeleteMixin, DeleteView
):
    model = VocabSource
    template_name = "{0}/auth/vocab_source_delete_confirm.html".format(APP_NAME)

    def get_object(self, **kwargs):
        return self.vocab_source

    def get_success_url(self):
        return reverse("vocab:vocab_sources")


class VocabSourceExportJsonView(
    LoginRequiredMixin, VocabSourceMixin,
    VocabSourceSessionMixin, VocabSourcePermissionMixin,
    JsonAttachmentMixin, View
):
    content_type = "application/json"
    json_indent = 2

    def get_file_content(self):
        vocab_source = get_object_or_404(
            VocabSource.objects.prefetch_related(
                "creator",
                "vocab_contexts__vocabcontextentry_set__vocab_entry"
            ),
            id=self.kwargs["vocab_source_pk"]
        )
        self.filename = "{0}.json".format(vocab_source.slug)
        data = export_vocab_source(self.request, vocab_source)

        return data
