from django.urls import include, path, re_path

from .views.views_vocab_auth import VocabUserDashboardView
from .views.views_vocab_context_auth import (
    VocabContextCreateView, VocabContextAudioCreateView,
    VocabContextTagView, VocabContextEntryTagView
)
from .views.views_vocab_entry import (
    VocabEntriesView, VocabEntryView
)
from .views.views_vocab_entry_auth import (
    VocabEntryCreateView, VocabEntryDeleteView,
    VocabEntryUpdateView
)
from .views.views_vocab_source import (
    VocabSourceContextsView,
    VocabSourceDashboardView, VocabSourceEntriesView,
    VocabSourceEntryView, VocabSourcesView
)
from .views.views_vocab_source_auth import (
    VocabSourceCreateView, VocabSourceDeleteView, VocabSourceExportJsonView,
    VocabSourceUpdateView, VocabSourcesView as VocabSourcesAuthView
)
from .views.views_vocab_autocomplete import (
    VocabEntryAutocompleteView,
    VocabSourceAutocompleteView, VocabSourceCreatorAutocompleteView,
    VocabSourceEntryAutocompleteView
)


app_name = "vocab"

auth_urls = [
    path("", VocabUserDashboardView.as_view(), name="vocab_user_dashboard"),
    path(
        "source/create/",
        VocabSourceCreateView.as_view(),
        name="vocab_source_create"
    ),
    path("entry/create/", VocabEntryCreateView.as_view(), name="vocab_entry_create"),
    re_path(
        "^entry/(?P<vocab_entry_language>[a-z]{2})/(?P<vocab_entry_slug>[-\w]+)/update/$",
        VocabEntryUpdateView.as_view(),
        name="vocab_entry_update"
    ),
    path(
        "entry/<int:vocab_entry_pk>/delete/",
        VocabEntryDeleteView.as_view(),
        name="vocab_entry_delete"
    ),
    path(
        "sources/",
        VocabSourcesAuthView.as_view(),
        name="auth_vocab_sources"
    ),
    path(
        "source/<slug:vocab_source_slug>/update/",
        VocabSourceUpdateView.as_view(),
        name="vocab_source_update"
    ),
    path(
        "source/<int:vocab_source_pk>/delete/",
        VocabSourceDeleteView.as_view(),
        name="vocab_source_delete"
    ),
    path(
        "source/<int:vocab_source_pk>)/export/",
        VocabSourceExportJsonView.as_view(),
        name="vocab_source_export_json"
    ),
    path(
        "source/<slug:vocab_source_slug>/context/create",
        VocabContextCreateView.as_view(),
        name="vocab_context_create"
    ),
    path(
        "context/<int:vocab_context_pk>/edit/",
        VocabContextTagView.as_view(),
        name="vocab_context_tag"
    ),
    path(
        "context/<int:vocab_context_pk>/audio/create/",
        VocabContextAudioCreateView.as_view(),
        name="vocab_context_audio_create"
    ),
    path(
        "vocabcontextentry/<int:vocab_context_entry_pk>/tag/",
        VocabContextEntryTagView.as_view(),
        name="vocab_context_entry_tag"
    ),
]

urlpatterns = [
    path(
        "",
        VocabEntriesView.as_view(),
        name="vocab_entries"
    ),
    path(
        "autocomplete/entry",
        VocabEntryAutocompleteView.as_view(),
        name="vocab_entry_autocomplete"
    ),
    path(
        "autocomplete/entry/<slug:language>/",
        VocabEntryAutocompleteView.as_view(),
        name="vocab_entry_language_autocomplete"
    ),
    path(
        "autocomplete/source/",
        VocabSourceAutocompleteView.as_view(),
        name="vocab_source_autocomplete"
    ),
    path(
        "autocomplete/source/creator/",
        VocabSourceCreatorAutocompleteView.as_view(),
        name="vocab_source_creator_autocomplete"
    ),
    path(
        "autocomplete/source/<int:vocab_source_pk>/entry/",
        VocabSourceEntryAutocompleteView.as_view(),
        name="vocab_source_entry_autocomplete"
    ),
    path(
        "autocomplete/source/(<int:vocab_source_pk>/entry/<slug:language>/",
        VocabSourceEntryAutocompleteView.as_view(),
        name="vocab_source_entry_language_autocomplete"
    ),
    path(
        "entry/<slug:vocab_entry_language>/<slug:vocab_entry_slug>/",
        VocabEntryView.as_view(),
        name="vocab_entry"
    ),
    path(
        "sources/",
        VocabSourcesView.as_view(),
        name="vocab_sources"
    ),
    path(
        "source/<slug:vocab_source_slug>/",
        VocabSourceDashboardView.as_view(),
        name="vocab_source_dashboard"
    ),
    path(
        "source/<slug:vocab_source_slug>/contexts/",
        VocabSourceContextsView.as_view(),
        name="vocab_source_contexts"
    ),
    path(
        "source/<slug:vocab_source_slug>/entries/",
        VocabSourceEntriesView.as_view(),
        name="vocab_source_entries"
    ),
    path(
        "source/<slug:vocab_source_slug>/entry/<slug:vocab_entry_language>/<slug:vocab_entry_slug>/",
        VocabSourceEntryView.as_view(),
        name="vocab_source_entry"
    ),
    path("auth/", include(auth_urls)),
]
