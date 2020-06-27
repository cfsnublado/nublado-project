from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from core.views import CachedObjectMixin, ObjectSessionMixin
from ..conf import settings
from ..models import VocabContextEntry, VocabEntry, VocabSource


class PermissionMixin(object):
    superuser_override = True

    def dispatch(self, request, *args, **kwargs):
        has_permission = self.check_permission()

        if not has_permission:
            raise PermissionDenied

        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)

    def check_permission(self, *args, **kwargs):
        raise NotImplementedError("Method check_permission needs to be implemented.")


class VocabSourcePermissionMixin(PermissionMixin):

    def check_permission(self):
        has_permission = False

        if self.superuser_override:
            if self.request.user.is_superuser or self.vocab_source.creator_id == self.request.user.id:
                has_permission = True
        else:
            if self.vocab_source.creator_id == self.request.user.id:
                has_permission = True

        return has_permission


class VocabSourceSessionMixin(ObjectSessionMixin):
    session_obj = "vocab_source"
    session_obj_attrs = ["id", "name", "slug"]


class VocabSourceMixin(CachedObjectMixin):
    vocab_source_id = "vocab_source_pk"
    vocab_source_slug = "vocab_source_slug"
    vocab_source = None
    source_admin = False

    def dispatch(self, request, *args, **kwargs):
        self.get_vocab_source(request, *args, **kwargs)

        if request.user.is_superuser or request.user.id == self.vocab_source.creator_id:
            self.source_admin = True

        return super(VocabSourceMixin, self).dispatch(request, *args, **kwargs)

    def get_vocab_source(self, request, *args, **kwargs):
        if self.vocab_source_id in kwargs:
            self.vocab_source = get_object_or_404(
                VocabSource.objects.select_related("creator"),
                id=kwargs[self.vocab_source_id]
            )
        elif self.vocab_source_slug in kwargs:
            self.vocab_source = get_object_or_404(
                VocabSource.objects.select_related("creator"),
                slug=kwargs[self.vocab_source_slug]
            )
        else:
            obj = self.get_object()

            if hasattr(obj, "vocab_source_id"):
                self.vocab_source = obj.vocab_source
            elif isinstance(obj, VocabSource):
                    self.vocab_source = obj
            else:
                raise Http404("Vocab source not found.")

    def get_context_data(self, **kwargs):
        context = super(VocabSourceMixin, self).get_context_data(**kwargs)
        context["vocab_source"] = self.vocab_source
        context["source_admin"] = self.source_admin

        return context


class VocabSourceSearchMixin(object):
    search_term = None
    vocab_source = None

    def dispatch(self, request, *args, **kwargs):
        self.search_term = self.request.GET.get("source", None)
        if self.search_term:
            try:
                self.vocab_source = VocabSource.objects.select_related("creator").get(
                    **self.get_search_query_kwargs()
                )

                return self.search_success(**kwargs)
            except VocabSource.DoesNotExist:
                print("Entry doesn't exist.")

        return super(VocabSourceSearchMixin, self).dispatch(request, *args, **kwargs)

    def get_search_query_kwargs(self):
        return {
            "name__iexact": self.search_term
        }

    def search_success(self, **kwargs):
        return redirect(
            "vocab:vocab_source_dashboard",
            vocab_source_slug=self.vocab_source.slug
        )

    def get_context_data(self, **kwargs):
        context = super(VocabSourceSearchMixin, self).get_context_data(**kwargs)
        context["vocab_source"] = self.vocab_source
        context["search_term"] = self.search_term

        return context


class VocabSourceSearchAuthMixin(VocabSourceSearchMixin):

    def get_search_query_kwargs(self):
        return {
            "creator_id": self.request.user.id,
            "name__iexact": self.search_term,
        }


class VocabEntryPermissionMixin(PermissionMixin):

    def check_permission(self):
        has_permission = False

        if self.request.user.is_superuser:
            has_permission = True

        return has_permission


class VocabEntrySessionMixin(ObjectSessionMixin):
    session_obj = "vocab_entry"
    session_obj_attrs = ["id", "language", "entry", "slug"]


class VocabEntryMixin(CachedObjectMixin):
    vocab_entry_id = "vocab_entry_pk"
    vocab_entry_language = "vocab_entry_language"
    vocab_entry_slug = "vocab_entry_slug"

    def dispatch(self, request, *args, **kwargs):
        if self.vocab_entry_id in kwargs:
            self.vocab_entry = get_object_or_404(
                VocabEntry,
                id=kwargs[self.vocab_entry_id]
            )
        elif self.vocab_entry_language in kwargs and self.vocab_entry_slug in kwargs:
            self.vocab_entry = get_object_or_404(
                VocabEntry,
                language=kwargs[self.vocab_entry_language],
                slug=kwargs[self.vocab_entry_slug]
            )
        else:
            obj = self.get_object()
            if hasattr(obj, "vocab_entry_id"):
                self.vocab_entry = obj.vocab_entry
            else:
                self.vocab_entry = obj

        return super(VocabEntryMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VocabEntryMixin, self).get_context_data(**kwargs)
        context["vocab_entry"] = self.vocab_entry

        return context


class VocabEntrySearchMixin(object):
    search_term = None
    search_language = "en"
    vocab_entry = None
    vocab_entry_redirect_url = "vocab:vocab_entry"

    def dispatch(self, request, *args, **kwargs):
        self.vocab_entry = self.get_search_entry()

        if self.vocab_entry:
            return self.search_success(**kwargs)

        return super(VocabEntrySearchMixin, self).dispatch(request, *args, **kwargs)

    def get_search_entry(self, **kwargs):
        self.search_term = self.request.GET.get("search_entry", None)
        self.search_language = self.request.GET.get("search_language", "en")

        if self.search_language not in settings.LANGUAGES_DICT:
            self.search_language = "en"

        if self.search_term and self.search_language:
            try:
                vocab_entry = VocabEntry.objects.get(
                    **self.get_search_query_kwargs()
                )

                return vocab_entry
            except VocabEntry.DoesNotExist:
                return None
        else:
            return None

    def get_search_query_kwargs(self):
        return {
            "entry__iexact": self.search_term,
            "language": self.search_language
        }

    def search_success(self, **kwargs):
        if self.vocab_entry and self.vocab_entry_redirect_url:
            return redirect(
                self.vocab_entry_redirect_url,
                vocab_entry_language=self.vocab_entry.language,
                vocab_entry_slug=self.vocab_entry.slug
            )

    def get_context_data(self, **kwargs):
        context = super(VocabEntrySearchMixin, self).get_context_data(**kwargs)
        context["vocab_entry"] = self.vocab_entry
        context["search_term"] = self.search_term
        context["search_language"] = self.search_language

        return context


class VocabSourceEntrySearchMixin(VocabEntrySearchMixin):
    search_source_id = None
    vocab_source = None
    vocab_entry_redirect_url = "vocab:vocab_source_entry"

    def get_search_entry(self, **kwargs):
        self.search_term = self.request.GET.get("search_entry", None)
        self.search_language = self.request.GET.get("search_language", "en")
        self.search_source_id = self.request.GET.get("search_source", None)

        if self.search_language not in settings.LANGUAGES_DICT:
            return None

        if self.search_term and self.search_language and self.search_source_id:
            try:
                vocab_context_entry = VocabContextEntry.objects.select_related(
                    "vocab_context",
                    "vocab_entry",
                    "vocab_context__vocab_source"
                ).distinct("vocab_entry_id").get(
                    **self.get_search_query_kwargs()
                )
                self.vocab_source = vocab_context_entry.vocab_context.vocab_source
                self.vocab_entry = vocab_context_entry.vocab_entry

                return self.vocab_entry
            except VocabContextEntry.DoesNotExist:
                return None
        else:
            return None

    def get_search_query_kwargs(self):
        return {
            "vocab_context__vocab_source_id": self.search_source_id,
            "vocab_entry__entry__iexact": self.search_term,
            "vocab_entry__language": self.search_language
        }

    def search_success(self, **kwargs):
        if self.vocab_entry and self.vocab_source and self.vocab_entry_redirect_url:
            return redirect(
                self.vocab_entry_redirect_url,
                vocab_source_slug=self.vocab_source.slug,
                vocab_entry_language=self.vocab_entry.language,
                vocab_entry_slug=self.vocab_entry.slug
            )
