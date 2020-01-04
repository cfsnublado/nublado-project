from rest_framework.authtoken import views
from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework.routers import DefaultRouter

from django.urls import path, re_path
from django.conf.urls import include

from users.api.views_api import UserViewSet, ProfileViewSet
from vocab.api.views_vocab_context import (
    NestedVocabContextEntryViewSet, NestedVocabContextViewSet,
    VocabContextEntryViewSet, VocabContextViewSet
)
from vocab.api.views_vocab_entry import (
    VocabEntryViewSet, VocabEntryExportView, VocabEntryInfoView,
    VocabEntryLanguageExportView, VocabEntryImportView
)
from vocab.api.views_vocab_source import (
    VocabSourceExportView, VocabSourceImportJSONView,
    VocabSourceImportMarkdownView, VocabSourceViewSet,
    VocabSourceEntryViewSet
)

from vocab.api.views_third_party_api import OxfordAPIEntryView

app_name = "app"

router = DefaultRouter()

# users
router.register("user", UserViewSet, basename="user")
router.register("profile", ProfileViewSet, basename="profile")
# vocab
router.register("entry", VocabEntryViewSet, basename="vocab-entry")
router.register("source", VocabSourceViewSet, basename="vocab-source")
router.register("vocab-context", VocabContextViewSet, basename="vocab-context")
router.register("vocab-context-entry", VocabContextEntryViewSet, basename="vocab-context-entry")

vocab_context_router = NestedSimpleRouter(router, "source", lookup="vocab_source")
vocab_context_router.register("vocab-context", NestedVocabContextViewSet, basename="nested-vocab-context")

vocab_entry_context_router = NestedSimpleRouter(router, "vocab-context", lookup="vocab_context")
vocab_entry_context_router.register(
    "vocab-context-entry",
    NestedVocabContextEntryViewSet,
    basename="nested-vocab-context-entry"
)

vocab_source_entry_list = VocabSourceEntryViewSet.as_view({"get": "list"})

urlpatterns = [
    path("api-token-auth/", views.obtain_auth_token, name="auth_token"),
    path("oxford/entry/", OxfordAPIEntryView.as_view(), name="oxford_entry"),
    path("vocab/entry/<int:vocab_entry_pk>/info/", VocabEntryInfoView.as_view(), name="vocab_entry_info"),
    path(
        "source/<int:vocab_source_pk>/entry/",
        vocab_source_entry_list,
        name="vocab-source-entry-list"
    ),
    path(
        "vocab/source/import/",
        VocabSourceImportJSONView.as_view(),
        name="vocab_source_import_json"
    ),
    path(
        "vocab/source/import/markdown/",
        VocabSourceImportMarkdownView.as_view(),
        name="vocab_source_import_markdown"
    ),
    path(
        "vocab/source/<int:vocab_source_pk>/export/",
        VocabSourceExportView.as_view(),
        name="vocab_source_export"
    ),
    path("vocab/entries/import/", VocabEntryImportView.as_view(), name="vocab_entries_import"),
    path("vocab/entries/export/", VocabEntryExportView.as_view(), name="vocab_entries_export"),
    re_path(
        "^vocab/entries/export/language/(?P<language>[a-z]{2})/$",
        VocabEntryLanguageExportView.as_view(),
        name="vocab_entries_language_export"
    ),
    path("", include(router.urls)),
    path("", include(vocab_context_router.urls)),
    path("", include(vocab_entry_context_router.urls)),
]
